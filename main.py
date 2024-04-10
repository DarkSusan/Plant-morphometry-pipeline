from plantcv import plantcv as pcv
from Image import Image
from plantcv.parallel import WorkflowInputs
import json
import os
import glob
import inquirer
import threading
import image_watcher
import ui


def interactive():
    img_path = inquirer.prompt(
        [
            inquirer.Path(
                "img_path",
                message="Enter image or directory path",
                default="images",
            )
        ]
    )["img_path"]

    # Check if the input is a directory
    if os.path.isdir(img_path):
        # Get all image files in the directory
        image_files = glob.glob(os.path.join(img_path, "*"))
        # Use the filenames as the names
        names = [
            os.path.basename(img_file).split(".")[0]
            for img_file in image_files
        ]
    else:
        # The input is a single image file
        image_files = [img_path]
        # Use the filename as the name
        names = [os.path.basename(img_path).split(".")[0]]

    # Write the image files and names to a configuration file
    image_names = ",".join(names)
    config = {
        "images": image_files,
        "names": image_names,
        "result": "results.json",
        "debug": "print",
        "debug_outdir": "./debug_plots",
    }

    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    # Use the data in your code
    args_init = WorkflowInputs(
        images=config["images"],
        names=config["names"],
        result=config["result"],
        debug=config["debug"],
        debug_outdir=config["debug_outdir"],
    )

    pcv.params.debug = args_init.debug
    pcv.params.text_size = 50
    pcv.params.text_thickness = 15
    pcv.params.debug_outdir = "./.tmp_debug_plots"

    os.makedirs(config["debug_outdir"], exist_ok=True)

    print("Reading the image...")

    img, path, filename = pcv.readimage(filename=args_init.plancik)
    img = Image(img, img_path)

    while True:
        match ui.get_function():
            case "crop image":
                mode = input(
                    "Would you like to input the coordinates manually? (y/N): "
                ).lower()
                if mode == "y":
                    img.crop_image(**ui.get_coordinates())
                else:
                    coordinates = img.get_coordinates()
                    img.crop_image(
                        coordinates["x"],
                        coordinates["y"],
                        coordinates["height"],
                        coordinates["width"],
                    )
                continue
            case "rotate image":
                img = img.rotate_image(
                    inquirer.Text("angle", message="Enter the angle: ")
                )
                continue
            case "analysis with color card":
                rgb_img = img
                mode = input(
                    "Would you like to input region of interest the coordinates manually? (y/N): "
                ).lower()

                roi = rgb_img.region_of_interest(**ui.get_coordinates())
                if mode == "y":
                    roi = rgb_img.region_of_interest(**ui.get_coordinates())
                    rgb_img.color_card_analysis().basic_rgb_analysis(roi)
                else:
                    coordinates = rgb_img.get_coordinates()
                    roi = rgb_img.region_of_interest(
                        coordinates["x"],
                        coordinates["y"],
                        coordinates["height"],
                        coordinates["width"],
                    )
                    rgb_img.color_card_analysis().basic_rgb_analysis(roi)

                img.save_json(img_path)
            case "analysis without color card":
                mode = input(
                    "Would you like to input region of interest the coordinates manually? (y/N): "
                ).lower()
                if mode == "y":
                    roi = img.region_of_interest(**ui.get_coordinates())
                    img.basic_rgb_analysis(roi)
                else:
                    coordinates = img.get_coordinates()
                    roi = img.region_of_interest(
                        coordinates["x"],
                        coordinates["y"],
                        coordinates["height"],
                        coordinates["width"],
                    )
                    img.basic_rgb_analysis(roi)

                img.save_json()
            case "watershed segmentation":
                img.watershed_segmentation()
                img.save_json("watershed_segmentation")
            case "quit":
                print("Quitting...")
                os.system(
                    f"rsync -a --delete .tmp_debug_plots/ {config['debug_outdir']}"
                )
                os.system(f"rm -r .tmp_debug_plots")
                exit("Goodbye!")


def main():
    ensure_directory_exists("./.tmp_debug_plots")
    watcher_thread = threading.Thread(
        target=image_watcher.watch_debug_plots, daemon=True
    )
    watcher_thread.start()

    match ui.get_mode():
        case "config file":
            exit(
                "Config file mode is not implemented yet. Please choose 'interactive mode'."
            )
        case "interactive mode":
            interactive()


if __name__ == "__main__":
    main()
