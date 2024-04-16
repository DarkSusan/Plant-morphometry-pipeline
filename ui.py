import inquirer
import shutil


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
                "watershed segmentation",
                "quit",
            ],
            carousel=True),
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
                "visualize colorspaces",
                "Create grayscale image",
                "auto threshold",
                "fill image",
                "return"
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
    feh_installed = shutil.which('feh') is not None

    # Define the options
    options = ['Dark Background']
    if feh_installed:
        options.append('Show images')

    questions = [
        inquirer.Checkbox(
            'options',
            message="Which options would you like to toggle?",
            choices=options,
            default=['Dark Background', 'Show images'] if feh_installed else ['Background Dark'],
            carousel=True
        ),

    ]

    return inquirer.prompt(questions)["options"]


def get_rgb_analysis():
    questions = [
        inquirer.List(
            "rgb_analysis",
            message="Would you like to analyze the image with a color card?",
            choices=["Analysis with color card", "Analysis without color card"],
        )
    ]

    return inquirer.prompt(questions)["rgb_analysis"]

def get_colorspaces():
    questions = [
        inquirer.List(
            "colorspaces",
            message="Which colorspace would you like to use for conversion?",
            choices=['CMYK', 'HSV', 'LAB'],
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