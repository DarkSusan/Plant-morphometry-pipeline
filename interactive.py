import ui
import copy
from workflow import *


def interactive(checkbox):
    pcv.params.debug = "print"
    pcv.params.text_size = 50
    pcv.params.text_thickness = 15
    pcv.params.debug_outdir = "./.tmp_debug_plots"

    if 'Dark Background' in checkbox:
        background = "dark"
    else:
        background = "light"

    for img_file in read_image():
        img = get_images(img_file, background)
        while True:
            match ui.get_function():
                case "image processing":
                    while True:
                        match ui.get_image_processing():
                            case "crop image":
                                mode = ui.get_region_input_method()
                                if mode == "Draw on interface":
                                    coordinates = img.get_coordinates()
                                    img.crop_image(
                                        coordinates["x"],
                                        coordinates["y"],
                                        coordinates["height"],
                                        coordinates["width"], )
                                else:
                                    img.crop_image(**ui.get_coordinates())
                                continue
                            case "rotate image":
                                img = img.rotate_image(ui.get_integer_input(
                                    inquirer.Text("angle", message="Enter the angle: ")
                                ))
                                continue
                            case "color correction":
                                img.color_color_correction()
                            case "visualize colorspaces":
                                img.visualize_colorspaces()
                            case "Create grayscale image":
                                match ui.get_colorspaces():
                                    case "LAB":
                                        img.convert_lab(ui.get_LAB())
                                    case "HSV":
                                        img.convert_hsv(ui.get_HSV())
                                    case "CMYK":
                                        img.convert_cmyk(ui.get_CMYK())
                            case "Threshold Image":
                                match ui.get_threshold_method():
                                    case "Triangle auto threshold":
                                        xstep_val = int(inquirer.prompt([
                                            inquirer.Text("xstep_val",
                                                          message="Enter xstep value for triangle thresholding")
                                        ])["xstep_val"])
                                        img.triangle_auto_threshold(ui.get_integer_input(xstep_val))
                                    case "Otsu auto threshold":
                                        img.otsu_auto_threshold()
                            case "fill image":
                                area_size = int(inquirer.prompt([
                                    inquirer.Text("area_size", message="Enter minimum object area size in pixels")
                                ])["area_size"])
                                img.fill_image(ui.get_integer_input(area_size))
                            case "return":
                                break
                case "RGB analysis":
                    rgb_img = copy.deepcopy(img)
                    print("[!] Region of interest is needed")
                    mode = ui.get_region_input_method()
                    if mode == "Draw on interface":
                        coordinates = rgb_img.get_coordinates()
                        roi = rgb_img.region_of_interest(
                            coordinates["x"],
                            coordinates["y"],
                            coordinates["height"],
                            coordinates["width"],
                        )
                        rgb_img.basic_rgb_analysis(roi)
                    else:
                        roi = rgb_img.region_of_interest(**ui.get_coordinates())
                        rgb_img.basic_rgb_analysis(roi)

                        rgb_img.save_json("RGB_No_Card")
                case "watershed segmentation":
                    water_img = copy.deepcopy(img)
                    distance_val = int(inquirer.prompt([
                        inquirer.Text("distance_val", message="Enter distance value for watershed segmentation")
                    ])["distance_val"])
                    water_img.watershed_segmentation(distance_val)
                    water_img.save_json("watershed_segmentation")
                case "next image":
                    break
                case "quit":
                    img.save_json("Final")
                    print("Quitting...")
                    os.system(
                        f"rsync -a --delete .tmp_debug_plots/ ./debug_plots")
                    os.system(f"rm -r .tmp_debug_plots")
                    exit("Goodbye!")