import ui
from workflow import *
import interface
import shutil


def interactive(checkbox):
    pcv.params.debug = "print"
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
            pcv.params.text_size = 50
            pcv.params.text_thickness = 15
            match ui.get_function():
                case "image processing":
                    while True:
                        match ui.get_image_processing():
                            case "crop image":
                                interface.crop_image(img)
                                continue
                            case "rotate image":
                                interface.rotate_image(img)
                                continue
                            case "color correction":
                                img.color_correction()
                            case "threshold image":
                                interface.thresholding(img)
                            case "dilate mask":
                                questions = [
                                    inquirer.Text("count", message="Enter the number of iterations for dilation"),
                                    inquirer.Text("size", message="Enter the size of dilation")
                                ]
                                answers = inquirer.prompt(questions)
                                count = int(answers["count"])
                                size = int(answers["size"])
                                img.dilate_image(count, size)
                            case "roi filter on mask":
                                coordinates = img.get_coordinates()
                                roi = img.region_of_interest(coordinates["x"],
                                                             coordinates["y"],
                                                             coordinates["height"],
                                                             coordinates["width"])
                                img.roi_filter(roi)
                            case "fill image":
                                interface.fill_image(img)
                            case "return":
                                break
                case "RGB analysis":
                    interface.RGB_analysis(img)
                    img.save_json("_RGB")
                case "morphology analysis":
                    img.morphological_analysis()
                    img.save_json("_morphology")
                case "watershed segmentation":
                    color = inquirer.List("color", "Select what color is the plant on the thresholded image",
                                                   ["white", "black"])
                    color = inquirer.prompt([color])["color"]
                    interface.watershed_segmentation(img, color)
                    img.save_json("_watershed")
                case "visualize results":
                    interface.visualize_results(img)
                case "next image":
                    if not config:
                        config = img.get_config()
                    break
                case "quit":
                    print("Quitting...")
                    shutil.copytree(".tmp_debug_plots", "./debug_plots", dirs_exist_ok=True)
                    shutil.rmtree(".tmp_debug_plots")
                    exit("Goodbye!")
