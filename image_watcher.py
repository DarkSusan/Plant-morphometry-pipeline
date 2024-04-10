import time
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import subprocess


def watch_debug_plots(window_size=(800, 600)):
    win_size = f"{window_size[0]}x{window_size[1]}"

    def on_created(event):
        nonlocal win_size
        subprocess.run(["feh", "--geometry", win_size, "--scale-down", event.src_path])

    observer = Observer()
    event_handler = LoggingEventHandler()

    event_handler.on_closed = on_created
    observer.schedule(event_handler, ".tmp_debug_plots", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
