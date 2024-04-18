from plantcv import plantcv as pcv
from plantcv.parallel import WorkflowInputs
import json
import os
import inquirer
import glob
from Image import Image


def read_image():
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

    print("Reading the image...")

    return image_files


def get_images(img_file, background):
    img, path, filename = pcv.readimage(filename=img_file)
    img = Image(img, img_file, background)

    return img


def config(names, image_files):
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
