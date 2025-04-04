import inquirer
import shutil


def get_integer_input(prompt):
    while True:
        try:
            value = int(prompt)
            return value
        except ValueError:
            print("Invalid input. Please enter an integer.")


def get_mode():
    questions_mode = [
        inquirer.List(
            "mode",
            message="Would you like to use config file or proceed to interactive mode?",
            choices=["config file", "interactive mode"],
            carousel=True,
        )
    ]

    return inquirer.prompt(questions_mode)["mode"]


def get_function():
    questions_function = [
        inquirer.List(
            "function",
            message="What would you like to do?",
            choices=[
                "image processing",
                "RGB analysis",
                "morphology analysis",
                "watershed segmentation",
                "visualize results",
                "next image",
                "quit",
            ],
            carousel=True,
        ),
    ]

    return inquirer.prompt(questions_function)["function"]


def get_image_processing():
    questions_image_processing = [
        inquirer.List(
            "image_processing",
            message="What would you like to do?",
            choices=[
                "crop image",
                "rotate image",
                "color correction",
                "threshold image",
                "roi filter on mask",
                "dilate mask",
                "fill image",
                "return",
            ],
            carousel=True,
        )
    ]

    return inquirer.prompt(questions_image_processing)["image_processing"]


def get_coordinates():
    questions_coordinates = [
        inquirer.Text("x", message="Enter the x coordinate"),
        inquirer.Text("y", message="Enter the y coordinate"),
        inquirer.Text("h", message="Enter the height"),
        inquirer.Text("w", message="Enter the width"),
    ]

    answers = inquirer.prompt(questions_coordinates)

    if not all(val.isnumeric() for val in answers.values()):
        # TODO: value correctness checking
        raise Exception("Wrong values")

    return {k: int(v) for k, v in answers.items()}


def get_region_input_method():
    questions_input_method = [
        inquirer.List(
            "input_method",
            message="How would you like to specify the region?",
            choices=["Draw on interface", "Input values manually"],
            carousel=True,
        )
    ]

    return inquirer.prompt(questions_input_method)["input_method"]


def checkbox():
    # Check if 'feh' is installed
    feh_installed = shutil.which("feh") is not None

    # Define the options
    options = ["Dark Background"]
    if feh_installed:
        options.append("Show images")

    questions = [
        inquirer.Checkbox(
            "options",
            message="Which options would you like to toggle?",
            choices=options,
            default=(
                ["Dark Background", "Show images"]
                if feh_installed
                else ["Background Dark"]
            ),
            carousel=True,
        ),
    ]

    return inquirer.prompt(questions)["options"]


def get_rgb_analysis():
    questions = [
        inquirer.List(
            "rgb_analysis",
            message="Would you like to analyze the image with a color card?",
            choices=[
                "Analysis with color card",
                "Analysis without color card",
            ],
        )
    ]

    return inquirer.prompt(questions)["rgb_analysis"]


def get_colorspaces(selections):
    questions = [
        inquirer.List(
            "colorspaces",
            message="Which colorspace would you like to use for conversion?",
            choices=selections,
            carousel=True,
        )
    ]
    return inquirer.prompt(questions)["colorspaces"]


def get_visualization_colorspaces():
    questions = [
        inquirer.List(
            "colorspaces",
            message="Which colorspace would you like to use for visualization?",
            choices=["ALL", "RGB", "HSV", "LAB"],
            carousel=True,
        )
    ]
    return inquirer.prompt(questions)["colorspaces"]


def get_CMYK():
    questions = [
        inquirer.List(
            "channel",
            message="Which channel would you like to use for conversion?",
            choices=['C', 'M', 'Y', 'K'],
            carousel=True,
        )
    ]
    return inquirer.prompt(questions)["channel"]


def get_HSV():
    questions = [
        inquirer.List(
            "channel",
            message="Which channel would you like to use for conversion?",
            choices=['H', 'S', 'V'],
            carousel=True,
        )
    ]
    return inquirer.prompt(questions)["channel"]


def get_LAB():
    questions = [
        inquirer.List(
            "channel",
            message="Which channel would you like to use for conversion?",
            choices=['L', 'A', 'B'],
            carousel=True,
        )
    ]
    return inquirer.prompt(questions)["channel"]


def get_RGB():
    questions = [
        inquirer.List(
            "channel",
            message="Which channel would you like to use for conversion?",
            choices=['R', 'G', 'B'],
            carousel=True,
        )
    ]
    return inquirer.prompt(questions)["channel"]


def get_threshold_method():
    questions = [
        inquirer.List(
            "threshold_method",
            message="Which thresholding method would you like to use?",
            choices=[
                "Auto threshold",
                "Binary threshold",
                "Dual channel threshold",
                "return",
            ],
            carousel=True,
        )
    ]
    return inquirer.prompt(questions)["threshold_method"]


def get_auto_threshold():
    questions = [
        inquirer.List(
            "auto_threshold",
            message="Which auto thresholding method would you like to use?",
            choices=[
                "Select colorspace",
                "Triangle auto threshold",
                "Otsu auto threshold",
                "return",
            ],
            carousel=True,
        )
    ]
    return inquirer.prompt(questions)["auto_threshold"]


def get_binary_threshold():
    questions = [
        inquirer.List(
            "binary_threshold",
            message="What would you like to do?",
            choices=[
                "Visualize for threshold point",
                "Select colorspace",
                "Binary threshold",
                "return",
            ],
            carousel=True,
        )
    ]
    return inquirer.prompt(questions)["binary_threshold"]


def get_grayscale_selections():
    questions = [
        inquirer.List(
            "grayscale",
            message="What would you like to do?",
            choices=[
                "visualize colorspaces",
                "convert to grayscale",
                "return",
            ],
            carousel=True,
        )
    ]
    return inquirer.prompt(questions)["grayscale"]


def get_visualization():
    questions_mode = [
        inquirer.List(
            "visualization",
            message="What analysis would you like to visualize?",
            choices=["Color Analysis", "All Results"],
            carousel=True,
        )
    ]

    return inquirer.prompt(questions_mode)["visualization"]


def get_object_type():
    questions = [
        inquirer.List(
            "object_type",
            message="Is your plant light or dark in grayscale image?",
            choices=["light", "dark"],
            carousel=True,
        )
    ]
    return inquirer.prompt(questions)["object_type"]


def get_color_scatter_plot():
    questions = [
        inquirer.List(
            "dual_channel_selection",
            message="What would you like to do?",
            choices=[
                "Select colorspaces",
                "visualize colorspaces in scatter plot",
                "Create mask",
                "return",
            ],
            carousel=True,
        )
    ]
    return inquirer.prompt(questions)["dual_channel_selection"]


def get_points():
    cords = inquirer.prompt(
        [
            inquirer.Text(
                "coords",
                message="Enter points separated by comma or space: ",
                default="80 80 125 40",
            )
        ]
    )

    position = inquirer.prompt(
        [
            inquirer.List(
                "position",
                message="Is the region where you want to apply threshold above or below the line?",
                choices=["above", "below"],
                carousel=True,
            )
        ]
    )

    if position["position"] == "above":
        position["position"] = True
    else:
        position["position"] = False

    return [cords, position]


