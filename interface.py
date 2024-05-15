import inquirer
import ui
import re


def grayscale_image(img):
    match ui.get_colorspaces(["LAB", "HSV", "CMYK"]):
        case "LAB":
            img.convert_lab(ui.get_LAB())
        case "HSV":
            img.convert_hsv(ui.get_HSV())
        case "CMYK":
            img.convert_cmyk(ui.get_CMYK())


def colorspace_selection(img):
    while True:
        match ui.get_grayscale_selections():
            case "visualize colorspaces":
                img.visualize_colorspaces()
            case "convert to grayscale":
                grayscale_image(img)
            case "return":
                break


def thresholding(img):
    while True:
        match ui.get_threshold_method():
            case "Auto threshold":
                auto_threshold(img)
            case "Binary threshold":
                while True:
                    match ui.get_binary_threshold():
                        case "Visualize for threshold point":
                            img.visualize_colorspace()
                        case "Select colorspace":
                            colorspace_selection(img)
                        case "Binary threshold":
                            binary_theshold(img)
                        case "return":
                            break
            case "Dual channel threshold":
                dual_channel_threshold(img)
            case "return":
                break


def auto_threshold(img):
    while True:
        match ui.get_auto_threshold():
            case "Select colorspace":
                colorspace_selection(img)
            case "Triangle auto threshold":
                if img.gray is None:
                    print("[!] Image is not in grayscale. Converting to grayscale...")
                    img.visualize_colorspaces()
                    grayscale_image(img)
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
                try:
                    img.triangle_auto_threshold(
                        ui.get_integer_input(xstep_val),
                        ui.get_object_type(),)
                except ValueError:
                    print("Invalid input. Please try again.")
                    continue
            case "Otsu auto threshold":
                if img.gray is None:
                    print("[!] Image is not in grayscale. Converting to grayscale...")
                    img.visualize_colorspaces()
                    grayscale_image(img)
                img.otsu_auto_threshold(
                    ui.get_object_type()
                )
            case "return":
                return


def dual_channel_threshold(img):
    x_channel, y_channel = None, None
    while True:
        match ui.get_color_scatter_plot():
            case "Select colorspaces":
                selections = ["HSV", "LAB", "RGB", "gray", "index"]
                match ui.get_colorspaces(selections):
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
                    case "gray":
                        x_channel = "gray"
                    case "index":
                        x_channel = "index"
                match ui.get_colorspaces(selections):
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
                    case "gray":
                        y_channel = "gray"
                    case "index":
                        y_channel = "index"
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
                points, placement = ui.get_points()
                points = points['coords']
                pattern = r"\b\d{1,3}\b"
                points = [
                    int(point)
                    for point in re.findall(
                        pattern, points
                    )
                ]
                print(points)

                if x_channel or y_channel is None:
                    print(
                        "\n\n [!] You need to select colorspaces first!"
                    )
                    continue
                try:
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
                        placement['position']
                    )
                except ValueError:
                    print("\n\n [!] Invalid input. Please try again.")
                    continue
            case "return":
                break


def binary_theshold(img):
    try:
        threshold_val = int(
            inquirer.prompt(
                [
                    inquirer.Text(
                        "threshold_val",
                        message="Enter threshold value for binary thresholding",
                    )
                ]
            )["threshold_val"]
        )
    except ValueError:
        print("Invalid input. Please try again.")
        return
    img.binary_threshold(
        threshold_val,
        ui.get_object_type(),
    )


def crop_image(img):
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


def rotate_image(img):
    img.rotate_image(
        ui.get_integer_input(
            inquirer.Text(
                "angle",
                message="Enter the angle: ",
            )
        )
    )


def fill_image(img):
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


def RGB_analysis(img):
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
        roi = img.region_of_interest(
            **ui.get_coordinates()
        )
        img.basic_rgb_analysis(roi)

        img.save_json("RGB_No_Card")


def watershed_segmentation(img, color):
    try:
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
        img.watershed_segmentation(distance_val, color)
    except ValueError:
        print("Something went wrong. Please try again.")
        return


def visualize_results(img):
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
