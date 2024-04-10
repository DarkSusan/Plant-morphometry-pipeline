from plantcv import plantcv as pcv
from Image import Image
from plantcv.parallel import WorkflowInputs
import json
import os
import glob
import inquirer
import threading
import image_watcher


def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


questions_mode = [
    inquirer.List('mode',
                  message="Would you like to use config file or proceed to interactive mode?",
                  choices=["config file", "interactive mode"],
                  carousel=True)]

questions_function = [
    inquirer.List('function',
                  message="What would you like to do?",
                  choices=["crop image", "rotate image", "analysis with color card", "analysis without color card",
                           "watershed segmentation", "quit"],
                  carousel=True
                  ),
]

questions_coordinates = [
    inquirer.Text('x_val', message="Enter the x coordinate"),
    inquirer.Text('y_val', message="Enter the y coordinate"),
    inquirer.Text('h_val', message="Enter the height"),
    inquirer.Text('w_val', message="Enter the width"),
]

ensure_directory_exists("./.tmp_debug_plots")
watcher_thread = threading.Thread(target=image_watcher.watch_debug_plots, daemon=True)
watcher_thread.start()

answers = inquirer.prompt(questions_mode)

mode = answers['mode']
match mode:
    case "config file":
        exit("Config file mode is not implemented yet. Please choose 'interactive mode'.")
    case "interactive mode":
        # Ask the user for a directory or file path

        img_path = inquirer.prompt(
            [inquirer.Path('img_path', message='Enter image or directory path', default='images')])['img_path']

        # Check if the input is a directory
        if os.path.isdir(img_path):
            # Get all image files in the directory
            image_files = glob.glob(os.path.join(img_path, '*'))
            # Use the filenames as the names
            names = [os.path.basename(img_file).split(".")[0] for img_file in image_files]
        else:
            # The input is a single image file
            image_files = [img_path]
            # Use the filename as the name
            names = [os.path.basename(img_path).split(".")[0]]

        # Write the image files and names to a configuration file
        image_names = ", ".join(names)
        config = {
            "images": image_files,
            "names": image_names,
            "result": "results.json",
            "debug": "print",
            "debug_outdir": "./debug_plots",
        }

        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)

        # Load the configuration file
        with open('config.json') as f:
            config = json.load(f)

        # Use the data in your code
        args_init = WorkflowInputs(
            images=config['images'],
            names=config['names'],
            result=config['result'],
            debug=config['debug'],
            debug_outdir=config['debug_outdir']
        )

        print("Image files:", image_files)

        pcv.params.debug = args_init.debug
        pcv.params.text_size = 50
        pcv.params.text_thickness = 15
        pcv.params.debug_outdir = "./.tmp_debug_plots"
        ensure_directory_exists(config['debug_outdir'])

        print("Reading the image...")
        # for img_file in image_files:
        #    img, path, filename = pcv.readimage(filename=img_file)

        img, path, filename = pcv.readimage(filename=args_init.plancik)
        img = Image(img, img_path)
        while True:
            print(img)
            answers = inquirer.prompt(questions_function)
            function = answers['function']
            match function:
                case "crop image":
                    mode = input("Would you like to input the coordinates manually? (y/N): ").lower()
                    if mode == "y":
                        answers_coordinates = inquirer.prompt(questions_coordinates)
                        x_val = int(answers_coordinates['x_val'])
                        y_val = int(answers_coordinates['y_val'])
                        h_val = int(answers_coordinates['h_val'])
                        w_val = int(answers_coordinates['w_val'])
                        img.crop_image(x_val, y_val, h_val, w_val)
                    else:
                        coordinates = img.get_coordinates()
                        img.crop_image(coordinates["x"], coordinates["y"], coordinates["height"],
                                             coordinates["width"])

                    continue
                case "rotate image":
                    img = img.rotate_image(inquirer.Text('angle', message="Enter the angle: "))
                    continue
                case "analysis with color card":
                    rgb_img = img
                    mode = input("Would you like to input region of interest the coordinates manually? (y/N): ").lower()
                    if mode == "y":
                        answers_coordinates = inquirer.prompt(questions_coordinates)
                        x_val = int(answers_coordinates['x_val'])
                        y_val = int(answers_coordinates['y_val'])
                        h_val = int(answers_coordinates['h_val'])
                        w_val = int(answers_coordinates['w_val'])
                        roi = rgb_img.region_of_interest(x_val, y_val, h_val, w_val)
                        rgb_img.color_card_analysis().basic_rgb_analysis(roi)
                    else:
                        coordinates = rgb_img.get_coordinates()
                        roi = rgb_img.region_of_interest(coordinates["x"], coordinates["y"], coordinates["height"],
                                                     coordinates["width"])
                        rgb_img.color_card_analysis().basic_rgb_analysis(roi)

                    img.save_json(img_path)
                case "analysis without color card":
                    mode = input("Would you like to input region of interest the coordinates manually? (y/N): ").lower()
                    if mode == "y":
                        answers_coordinates = inquirer.prompt(questions_coordinates)
                        x_val = int(answers_coordinates['x_val'])
                        y_val = int(answers_coordinates['y_val'])
                        h_val = int(answers_coordinates['h_val'])
                        w_val = int(answers_coordinates['w_val'])
                        roi = img.region_of_interest(x_val, y_val, h_val, w_val)
                        img.basic_rgb_analysis(roi)
                    else:
                        coordinates = img.get_coordinates()
                        roi = img.region_of_interest(coordinates["x"], coordinates["y"],
                                                     coordinates["height"], coordinates["width"])
                        img.basic_rgb_analysis(roi)

                    img.save_json()
                case "watershed segmentation":
                    img.watershed_segmentation()
                    img.save_json("watershed_segmentation")
                case "quit":
                    print("Quitting...")
                    os.system(f"rsync -a --delete .tmp_debug_plots/ {config['debug_outdir']}")
                    os.system(f"rm -r .tmp_debug_plots")
                    exit("Goodbye!")
