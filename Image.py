import json
import os
import Coordinates_extractor as Coords
from functools import partial
from matplotlib import pyplot as plt
from plantcv import plantcv as pcv
import inquirer


class Image:
    def __init__(self, img, img_path, background, config=[]):
        self.img = img
        self.img_path = img_path
        self.background = background
        self.gray = None
        self.mask = None
        self.skeleton = None
        self.edge_objects = None
        self.leaf = None
        self.stem = None
        self.branch_points = None
        self.tip_points = None
        self.rgb_analysis = None
        self.watershed = None
        self.config = config
        self.has_config = True if config else False

    def run_config(self):
        for func in self.config:
            print(func)
            func(self)

    def get_config(self):
        return self.config

    def get_coordinates(self):
        return Coords.select_coordinates(self.img)

    def crop_image(self, x=0, y=0, h=0, w=0):
        remainder = w % 4

        if remainder != 0:
            w -= remainder

        self.img = pcv.crop(img=self.img, x=x, y=y, h=h, w=w)

        if not self.has_config:
            self.config.append(partial(Image.crop_image, x=x, y=y, h=h, w=w))

    def region_of_interest(self, x=0, y=0, h=0, w=0):
        return pcv.roi.rectangle(img=self.img, x=x, y=y, h=h, w=w)

    def region_of_interest_mask(self, x=0, y=0, h=0, w=0):
        return pcv.roi.rectangle(img=self.mask, x=x, y=y, h=h, w=w)

    def rotate_image(self, angle):
        self.img = pcv.transform.rotate(self.img, angle, False)

        if not self.has_config:
            self.config.append(partial(Image.rotate_image, angle=angle))

    def visualize_colorspaces(self):
        # Code to find the closest number divisible by 4 because visualize colorspaces is retarded
        width = self.img.shape[1]
        remainder = width % 4
        if remainder <= 2:
            new_width = width - remainder
        else:
            new_width = width + (4 - remainder)

        # Crop the image to the new width
        self.img = self.img[:, :new_width]
        print(self.img.shape)
        pcv.visualize.colorspaces(rgb_img=self.img, original_img=False)

        if not self.has_config:
            self.config.append(Image.visualize_colorspaces)

    def convert_lab(self, channel):
        self.gray = pcv.rgb2gray_lab(rgb_img=self.img, channel=channel)

        if not self.has_config:
            self.config.append(partial(Image.convert_lab, channel=channel))

    def convert_hsv(self, channel):
        self.gray = pcv.rgb2gray_hsv(rgb_img=self.img, channel=channel)

        if not self.has_config:
            self.config.append(partial(Image.convert_hsv, channel=channel))

    def convert_cmyk(self, channel):
        self.gray = pcv.rgb2gray_cmyk(rgb_img=self.img, channel=channel)

        if not self.has_config:
            self.config.append(partial(Image.convert_cmyk, channel=channel))

    def otsu_auto_threshold(self, obj):
        self.mask = pcv.threshold.otsu(
            gray_img=self.gray, object_type=obj
        )

        if not self.has_config:
            self.config.append(Image.otsu_auto_threshold)

    def triangle_auto_threshold(self, xstep_val, obj):
        self.mask = pcv.threshold.triangle(
            gray_img=self.gray, object_type=obj, xstep=xstep_val
        )

        if not self.has_config:
            self.config.append(Image.triangle_auto_threshold)

    def binary_threshold(self, threshold_val, obj):
        if self.gray is None:
            print("Please convert the image to grayscale first.")
            return
        self.mask = pcv.threshold.binary(gray_img=self.gray, threshold=threshold_val, object_type=obj)

        if not self.has_config:
            self.config.append(Image.binary_threshold)

    def dual_channel_threshold(self, x_ch, y_ch, pts, pts_placement):
        self.mask = pcv.threshold.dual_channels(
            rgb_img=self.img,
            x_channel=x_ch,
            y_channel=y_ch,
            points=pts,
            above=pts_placement,
        )

        if not self.has_config:
            self.config.append(Image.dual_channel_threshold)

    def roi_filter(self, roi):
        self.mask = pcv.roi.filter(mask=self.mask, roi=roi, roi_type="partial")

    def dilate_image(self, size, count):
        self.mask = pcv.dilate(gray_img=self.mask, ksize=size, i=count)

        if not self.has_config:
            self.config.append(partial(Image.dilate_image, size=size, count=count))

    def fill_image(self, area_size):
        self.mask = pcv.fill_holes(
            pcv.fill(bin_img=self.mask, size=area_size)
        )

        if not self.has_config:
            self.config.append(partial(Image.fill_image, area_size=area_size))

    def morphological_analysis(self):
        pcv.params.dpi = 100
        pcv.params.text_size = 1
        pcv.params.text_thickness = 2
        pcv.params.line_thickness = 3

        self.skeleton = pcv.morphology.skeletonize(self.mask)
        question = [
            inquirer.Text("prune", message="Enter the size of pruning")
        ]
        size = int(inquirer.prompt(question)["prune"])
        self.skeleton, seg_img, self.edge_objects = pcv.morphology.prune(skel_img=self.skeleton, size=size,
                                                                         mask=self.mask)
        while True:
            skel_edit = inquirer.list_input("Would you like to again edit the skeleton?", choices=["yes", "no"])
            match skel_edit:
                case "yes":
                    question = [
                        inquirer.Text("prune", message="Enter the size of pruning")
                    ]
                    size = int(inquirer.prompt(question)["prune"])
                    self.skeleton, _, self.edge_objects = pcv.morphology.prune(skel_img=self.skeleton, size=size,
                                                                               mask=self.mask)
                case "no":
                    break

        self.leaf, self.stem = pcv.morphology.segment_sort(skel_img=self.skeleton, objects=self.edge_objects,
                                                           mask=self.mask)
        pcv.morphology.fill_segments(mask=self.mask, objects=self.leaf, label="default")

        self.branch_points = pcv.morphology.find_branch_pts(skel_img=self.skeleton, mask=self.mask, label="default")

        self.tip_points = pcv.morphology.find_tips(skel_img=self.skeleton, mask=None, label="default")

        segmented_img, labeled_img = pcv.morphology.segment_id(skel_img=self.skeleton,
                                                               objects=self.leaf,
                                                               mask=self.mask)

        pcv.morphology.segment_path_length(segmented_img=segmented_img,
                                           objects=self.leaf, label="default")

        pcv.morphology.segment_euclidean_length(segmented_img=segmented_img,
                                                objects=self.leaf, label="default")

        pcv.morphology.segment_curvature(segmented_img=segmented_img,
                                         objects=self.leaf, label="default")

        pcv.morphology.segment_angle(segmented_img=segmented_img,
                                     objects=self.leaf, label="default")

        question = [
            inquirer.Text("segment_tangent", message="Enter the size of the tangent")
        ]
        size = int(inquirer.prompt(question)["segment_tangent"])

        pcv.morphology.segment_tangent_angle(segmented_img=segmented_img,
                                             objects=self.leaf, size=size, label="default")

        question = [
            inquirer.Text("segment_insertion_angle", message="Enter the size of the insertion angle")
        ]
        size = int(inquirer.prompt(question)["segment_insertion_angle"])

        pcv.morphology.segment_insertion_angle(skel_img=self.skeleton,
                                               segmented_img=segmented_img,
                                               leaf_objects=self.leaf,
                                               stem_objects=self.stem,
                                               size=size, label="default")

        pcv.analyze.size(img=self.img, labeled_mask=self.mask, label="default")

    def color_correction(
            self, radius_val=10, pos_val=3, nrows_val=6, ncols_val=4
    ):
        dataframe1, start1, space1 = pcv.transform.find_color_card(
            rgb_img=self.img,
            background=self.background,
        )
        card_mask = pcv.transform.create_color_card_mask(
            self.img,
            radius=radius_val,
            start_coord=start1,
            spacing=space1,
            nrows=nrows_val,
            ncols=ncols_val,
        )
        headers, card_matrix = pcv.transform.get_color_matrix(
            rgb_img=self.img, mask=card_mask
        )
        std_color_matrix = pcv.transform.std_color_matrix(pos=pos_val)
        self.img = pcv.transform.affine_color_correction(
            self.img, card_matrix, std_color_matrix
        )

        if not self.has_config:
            self.config.append(Image.color_correction)

    def basic_rgb_analysis(self, region_of_interest):
        kept_mask = pcv.roi.filter(
            mask=self.mask, roi=region_of_interest, roi_type="partial"
        )
        pcv.analyze.size(img=self.img, labeled_mask=kept_mask)
        pcv.analyze.bound_horizontal(
            img=self.img,
            labeled_mask=kept_mask,
            line_position=2380,
            label="default",
        )

        if not self.has_config:
            self.config.append(
                partial(
                    Image.basic_rgb_analysis,
                    region_of_interest=region_of_interest,
                )
            )

    def color_histogram(self, colorspace):
        pcv.analyze.color(
            rgb_img=self.img,
            labeled_mask=self.mask,
            colorspaces=colorspace,
            label="default",
        )
        pcv.visualize.histogram(img=self.img, mask=self.mask, hist_data=True)

    def scatter_plot(self, x_channel, y_channel):
        pcv.visualize.pixel_scatter_plot(
            paths_to_imgs=[self.img_path],
            x_channel=x_channel,
            y_channel=y_channel,
        )
        plt.show()

    def watershed_segmentation(self, distance_val, color_mask="light"):
        masked = pcv.apply_mask(
            img=self.img, mask=self.mask, mask_color=color_mask
        )
        pcv.watershed_segmentation(
            rgb_img=masked,
            mask=self.mask,
            distance=distance_val,
            label="default",
        )
        self.watershed = pcv.outputs.observations["default"][
            "estimated_object_count"
        ]["value"]

        if not self.has_config:
            self.config.append(
                partial(
                    Image.watershed_segmentation, distance_val=distance_val
                )
            )

    def visualize_colorspace(self):
        if self.gray is None:
            print("Please convert the image to grayscale first.")
            return
        pcv.visualize.histogram(self.gray)

    def save_json(self, suffix=""):
        filename = f"{os.path.splitext(os.path.basename(self.img_path))[0]}{suffix}_results.json"
        print("Saving the results...")
        pcv.outputs.save_results(filename)

        # Open the results.json file
        with open(filename) as f:
            data = json.load(f)

        # Write the formatted data back to the file
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
