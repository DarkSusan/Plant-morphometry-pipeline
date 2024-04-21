import threading
import image_watcher
import ui
from workflow import *
from interactive import interactive


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
            if "Show images" in checkbox_answers:
                watcher_thread = threading.Thread(
                    target=image_watcher.watch_debug_plots, daemon=True
                )
                watcher_thread.start()
            interactive(checkbox_answers)


if __name__ == "__main__":
    main()
