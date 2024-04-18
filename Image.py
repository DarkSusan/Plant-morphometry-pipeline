import json
import os
import Coordinates_extractor as Coords
from plantcv import plantcv as pcv


class Image:
    def __init__(self, img, img_path, background):
        self.img = img
        self.img_path = img_path
        self.background = background
        self.gray = None
        self.threshold = None
        self.mask = None

    def get_coordinates(self):
        return Coords.select_coordinates(self.img)

    def crop_image(self, x=0, y=0, h=0, w=0):
        self.img = pcv.crop(img=self.img, x=x, y=y, h=h, w=w)

    def region_of_interest(self, x=0, y=0, h=0, w=0):
        return pcv.roi.rectangle(img=self.img, x=x, y=y, h=h, w=w)

    def rotate_image(self, angle):
        self.img = pcv.transform.rotate(self.img, angle, False)

    def visualize_colorspaces(self):
        # Code to find the closest number divisible by 4 because visualize colorspaces is retarted
        remainder = self.img.shape[1] % 4
        if remainder <= 2:
            new_width = self.img.shape[1] - remainder
        else:
            new_width = self.img.shape[1] + (4 - remainder)

        # Crop the image to the new width
        self.img = self.img[:, :new_width]
        print(self.img.shape)
        pcv.visualize.colorspaces(rgb_img=self.img, original_img=False)

    def convert_lab(self, channel):
        self.gray = pcv.rgb2gray_lab(rgb_img=self.img, channel=channel)

    def convert_hsv(self, channel):
        self.gray = pcv.rgb2gray_hsv(rgb_img=self.img, channel=channel)

    def convert_cmyk(self, channel):
        self.gray = pcv.rgb2gray_cmyk(rgb_img=self.img, channel=channel)

    def otsu_auto_threshold(self):
        if self.background == 'light':
            obj = 'dark'
        else:
            obj = 'light'
        self.threshold = pcv.threshold.otsu(gray_img=self.gray, object_type=obj)

    def triangle_auto_threshold(self, xstep_val):
        if self.background == 'light':
            obj = 'dark'
        else:
            obj = 'light'
        self.threshold = pcv.threshold.triangle(gray_img=self.gray, object_type=obj, xstep=xstep_val)

    def fill_image(self, area_size):
        self.mask = pcv.fill_holes(pcv.fill(bin_img=self.threshold, size=area_size))

    def color_color_correction(self):
        dataframe1, start1, space1 = pcv.transform.find_color_card(rgb_img=self.img, background=self.background, )
        card_mask = pcv.transform.create_color_card_mask(self.img, radius=10, start_coord=start1, spacing=space1,
                                                         nrows=6, ncols=4)
        headers, card_matrix = pcv.transform.get_color_matrix(rgb_img=self.img, mask=card_mask)
        std_color_matrix = pcv.transform.std_color_matrix(pos=3)
        self.img = pcv.transform.affine_color_correction(self.img, card_matrix, std_color_matrix)

    def basic_rgb_analysis(self, region_of_interest):
        # thresh1 = pcv.threshold.dual_channels(rgb_img=self.img, x_channel="a", y_channel="b",
        #                                      points=[(80, 80), (125, 140)], above=True)
        kept_mask = pcv.roi.filter(mask=self.mask, roi=region_of_interest, roi_type='partial')
        pcv.analyze.size(img=self.img, labeled_mask=kept_mask)
        pcv.analyze.bound_horizontal(img=self.img, labeled_mask=kept_mask, line_position=2380, label="default")
        self.img = pcv.analyze.color(rgb_img=self.img, labeled_mask=kept_mask, colorspaces='all', label="default")

    def watershed_segmentation(self, distance_val):
        # a = pcv.rgb2gray_lab(rgb_img=self.img, channel='a')
        # img_binary = pcv.threshold.binary(gray_img=a, threshold=110, object_type='dark')
        # fill_image = pcv.fill(bin_img=self.threshold)
        if self.background == 'light':
            color_mask = 'BLACK'
        else:
            color_mask = 'WHITE'
        masked = pcv.apply_mask(img=self.img, mask=self.mask, mask_color=color_mask)
        pcv.watershed_segmentation(rgb_img=masked, mask=self.mask, distance=distance_val, label="default")
        self.img = pcv.outputs.observations["default"]["estimated_object_count"]["value"]

    def save_json(self, suffix=""):
        filename = f"{os.path.splitext(os.path.basename(self.img_path))[0]}{suffix}_results.json"
        print("Saving the results...")
        pcv.outputs.save_results(filename)

        # Open the results.json file
        with open(filename) as f:
            data = json.load(f)

        # Write the formatted data back to the file
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
