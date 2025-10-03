import tkinter as tk
from tkinter import ttk
from downloader.spotify import download_spotify
from downloader.youtube import download_youtube
from downloader.cache import clean_cache
from downloader.debug import debug_track
from downloader.cache import clean_cache
from gui.logger import log_message

class DownloadController:
    def __init__(self, progress_bar, log_box):
        self.paused = False
        self.cancelled = False
        self.progress_bar = progress_bar
        self.log_box = log_box

    def should_continue(self):
        return not self.cancelled

    def update_progress(self, fraction):
        self.progress_bar["value"] = fraction * 100
        self.progress_bar.update()

    def log(self, message, level="INFO"):
        log_message(self.log_box, message, level)

def start_download(platform, url, controller):
    controller.cancelled = False
    controller.paused = False
    controller.update_progress(0)
    controller.log(f"Starting {platform} download...", "INFO")

    # After download completes
cleaned = clean_cache()
controller.log(f"Cleaned {cleaned} leftover files.", "INFO")

# Optional: run debug inspection
if platform == "Spotify":
    search_query = url.split("/")[-1]  # or use actual track info if available
    from downloader.spotify import find_latest_flac
    flac_path = find_latest_flac()
    if flac_path:
        debug_track(search_query, flac_path, controller.log_box)

controller.log("Download session complete.", "SUCCESS")

def build_gui():
    root = tk.Tk()
    root.title("Dansanya14 Audio Protocol")

    tk.Label(root, text="Platform:").grid(row=0, column=0)
    platform_var = tk.StringVar(value="Spotify")
    platform_menu = ttk.Combobox(root, textvariable=platform_var, values=["Spotify", "YouTube"])
    platform_menu.grid(row=0, column=1)

    tk.Label(root, text="Playlist/Video URL:").grid(row=1, column=0)
    url_entry = tk.Entry(root, width=50)
    url_entry.grid(row=1, column=1)

    progress_bar = ttk.Progressbar(root, length=300)
    progress_bar.grid(row=2, column=0, columnspan=2, pady=10)

    log_box = tk.Text(root, height=15, width=60)
    log_box.grid(row=3, column=0, columnspan=2)
    log_box.tag_config("INFO", foreground="blue")
    log_box.tag_config("SUCCESS", foreground="green")
    log_box.tag_config("WARNING", foreground="orange")
    log_box.tag_config("ERROR", foreground="red")

    controller = DownloadController(progress_bar, log_box)

    def on_start():
        url = url_entry.get()
        platform = platform_var.get()
        start_download(platform, url, controller)

    def on_pause():
        controller.paused = True
        controller.log("Paused...", "INFO")

    def on_resume():
        controller.paused = False
        controller.log("Resumed...", "INFO")

    def on_cancel():
        controller.cancelled = True
        controller.log("Cancelled by user.", "WARNING")

    tk.Button(root, text="Start", command=on_start).grid(row=4, column=0)
    tk.Button(root, text="Pause", command=on_pause).grid(row=4, column=1)
    tk.Button(root, text="Resume", command=on_resume).grid(row=5, column=0)
    tk.Button(root, text="Cancel", command=on_cancel).grid(row=5, column=1)

    root.mainloop()

if __name__ == "__main__":
    build_gui()
