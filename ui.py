import inquirer


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
                "crop image",
                "rotate image",
                "analysis with color card",
                "analysis without color card",
                "watershed segmentation",
                "quit",
            ],
            carousel=True,
        ),
    ]

    return inquirer.prompt(questions_function)["function"]


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
        raise Exception("u no has brain?")

    return {k: int(v) for k, v in answers.items()}
