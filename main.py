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
import copy


def interactive(checkbox):
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
        "result": "./results/results.json",
        "debug": "print",
        "debug_outdir": "./debug_plots",
        "background": "dark",
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
        background=config["background"],
    )

    pcv.params.debug = args_init.debug
    pcv.params.text_size = 50
    pcv.params.text_thickness = 15
    pcv.params.debug_outdir = "./.tmp_debug_plots"

    os.makedirs(config["debug_outdir"], exist_ok=True)

    print("Reading the image...")

    if 'Dark Background' in checkbox:
        background = "dark"
    else:
        background = "light"

    img, path, filename = pcv.readimage(filename=args_init.plancik)
    img = Image(img, img_path, background)

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
                            img = img.rotate_image(
                                inquirer.Text("angle", message="Enter the angle: ")
                            )
                            continue
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
                        case "auto threshold":
                            img.auto_threshold()
                        case "fill image":
                            area_size = int(inquirer.prompt([
                                inquirer.Text("area_size", message="Enter minimum object area size in pixels")
                            ])["area_size"])
                            img.fill_image(area_size)
                        case "return":
                            break
            case "RGB analysis":
                rgb_img = copy.deepcopy(img)
                match ui.get_rgb_analysis():
                    case "Analysis with color card":
                        print("[!] Region of interest is needed")
                        mode = ui.get_region_input_method()

                        if mode == "Draw on interface":
                            coordinates = rgb_img.get_coordinates()
                            roi = rgb_img.region_of_interest(
                                coordinates["x"],
                                coordinates["y"],
                                coordinates["height"],
                                coordinates["width"], )
                            rgb_img.color_card_analysis().basic_rgb_analysis(roi)
                        else:
                            roi = rgb_img.region_of_interest(**ui.get_coordinates())
                            rgb_img.color_card_analysis().basic_rgb_analysis(roi)

                        rgb_img.save_json("RGB_With_Card")
                    case "Analysis without color card":
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
                water_img.watershed_segmentation()
                water_img.save_json("watershed_segmentation")
            case "quit":
                print("Quitting...")
                os.system(
                    f"rsync -a --delete .tmp_debug_plots/ {config['debug_outdir']}"
                )
                os.system(f"rm -r .tmp_debug_plots")
                exit("Goodbye!")


def main():
    os.makedirs("./.tmp_debug_plots", exist_ok=True)

    match ui.get_mode():
        case "config file":
            exit(
                "Config file mode is not implemented yet. Please choose 'interactive mode'."
            )
        case "interactive mode":
            checkbox_answers = ui.checkbox()
            print(checkbox_answers)
            if 'Show images' in checkbox_answers:
                watcher_thread = threading.Thread(
                    target=image_watcher.watch_debug_plots, daemon=True
                )
                watcher_thread.start()
            interactive(checkbox_answers)


if __name__ == "__main__":
    main()
