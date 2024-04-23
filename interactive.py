import ui
import re
from workflow import *


def interactive(checkbox):
    pcv.params.debug = "print"
    pcv.params.text_size = 50
    pcv.params.text_thickness = 15
    pcv.params.debug_outdir = "./.tmp_debug_plots"

    if "Dark Background" in checkbox:
        background = "dark"
    else:
        background = "light"

    config = []

    for img_file in read_image():
        img = get_image(img_file, background, config)

        if config:
            print("Repeating analysis from previous run...")
            img.run_config()
            continue

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
                                        coordinates["width"],
                                    )
                                else:
                                    img.crop_image(**ui.get_coordinates())
                                continue
                            case "rotate image":
                                img = img.rotate_image(
                                    ui.get_integer_input(
                                        inquirer.Text(
                                            "angle",
                                            message="Enter the angle: ",
                                        )
                                    )
                                )
                                continue
                            case "color correction":
                                img.color_correction()
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
                                        xstep_val = int(
                                            inquirer.prompt(
                                                [
                                                    inquirer.Text(
                                                        "xstep_val",
                                                        message="Enter xstep value for triangle thresholding",
                                                    )
                                                ]
                                            )["xstep_val"]
                                        )
                                        img.triangle_auto_threshold(
                                            ui.get_integer_input(xstep_val),
                                            ui.get_object_type(),
                                        )
                                    case "Otsu auto threshold":
                                        img.otsu_auto_threshold(
                                            ui.get_object_type()
                                        )
                                    case "Dual channel threshold":
                                        x_channel, y_channel = None, None
                                        while True:
                                            match ui.get_color_scatter_plot():
                                                case "Select colorspaces":
                                                    match ui.get_colorspaces(
                                                        ["HSV", "LAB", "RGB"]
                                                    ):
                                                        case "LAB":
                                                            x_channel = (
                                                                ui.get_LAB().lower()
                                                            )
                                                        case "HSV":
                                                            x_channel = (
                                                                ui.get_HSV().lower()
                                                            )
                                                        case "RGB":
                                                            x_channel = (
                                                                ui.get_RGB()
                                                            )
                                                    match ui.get_colorspaces(
                                                        ["HSV", "LAB", "RGB"]
                                                    ):
                                                        case "LAB":
                                                            y_channel = (
                                                                ui.get_LAB().lower()
                                                            )
                                                        case "HSV":
                                                            y_channel = (
                                                                ui.get_HSV().lower()
                                                            )
                                                        case "RGB":
                                                            y_channel = (
                                                                ui.get_RGB()
                                                            )
                                                case "visualize colorspaces in scatter plot":
                                                    if not all(
                                                        (x_channel, y_channel)
                                                    ):
                                                        print(
                                                            "You need to select colorspaces first!"
                                                        )
                                                        continue
                                                    img.scatter_plot(
                                                        x_channel, y_channel
                                                    )
                                                case "Create mask":
                                                    points = inquirer.prompt(
                                                        [
                                                            inquirer.Text(
                                                                "points",
                                                                message="Enter points in brackets separated by commas",
                                                                default="(80, 80),(125,140)",
                                                            )
                                                        ]
                                                    )["points"]

                                                    pattern = r"\b\d{1,3}\b"
                                                    points = [
                                                        int(point)
                                                        for point in re.findall(
                                                            pattern, points
                                                        )
                                                    ]
                                                    print(points)

                                                    img.dual_channel_threshold(
                                                        x_channel,
                                                        y_channel,
                                                        [
                                                            (
                                                                points[0],
                                                                points[1],
                                                            ),
                                                            (
                                                                points[2],
                                                                points[3],
                                                            ),
                                                        ],
                                                    )
                                                    break

                            case "fill image":
                                area_size = int(
                                    inquirer.prompt(
                                        [
                                            inquirer.Text(
                                                "area_size",
                                                message="Enter minimum object area size in pixels",
                                            )
                                        ]
                                    )["area_size"]
                                )
                                img.fill_image(ui.get_integer_input(area_size))
                            case "return":
                                break
                case "RGB analysis":
                    print("[!] Region of interest is needed")
                    mode = ui.get_region_input_method()
                    if mode == "Draw on interface":
                        coordinates = img.get_coordinates()
                        roi = img.region_of_interest(
                            coordinates["x"],
                            coordinates["y"],
                            coordinates["height"],
                            coordinates["width"],
                        )
                        img.basic_rgb_analysis(roi)
                    else:
                        roi = img.region_of_interest(**ui.get_coordinates())
                        img.basic_rgb_analysis(roi)

                        img.save_json("RGB_No_Card")

                case "watershed segmentation":
                    distance_val = int(
                        inquirer.prompt(
                            [
                                inquirer.Text(
                                    "distance_val",
                                    message="Enter distance value for watershed segmentation",
                                )
                            ]
                        )["distance_val"]
                    )
                    img.watershed_segmentation(distance_val)
                    img.save_json("watershed_segmentation")
                case "visualize results":
                    match ui.get_visualization():
                        case "Color Analysis":
                            match ui.get_visualization_colorspaces():
                                case "ALL":
                                    img.color_histogram("all")
                                case "RGB":
                                    img.color_histogram("RGB")
                                case "LAB":
                                    img.color_histogram("LAB")
                                case "HSV":
                                    img.color_histogram("HSV")

                case "next image":
                    if not config:
                        config = img.get_config()
                    break
                case "quit":
                    img.save_json("Final")
                    print("Quitting...")
                    os.system(
                        f"rsync -a --delete .tmp_debug_plots/ ./debug_plots"
                    )
                    os.system(f"rm -r .tmp_debug_plots")
                    exit("Goodbye!")
