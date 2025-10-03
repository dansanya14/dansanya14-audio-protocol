import tkinter as tk
from gui.controller import Controller
from gui.logger import log_message
from gui.cache_cleaner import clean_cache
from downloader.spotify import download_spotify
from downloader.youtube import download_youtube

def launch_gui():
    controller = Controller()
    root = tk.Tk()
    root.title("Dansanya14's Audio Protocol")

    log_box = tk.Text(root, height=10, width=80)
    log_box.pack()

    def run_spotify():
        url = url_entry.get()
        download_spotify(url, controller, log_box)

    def run_youtube():
        url = url_entry.get()
        download_youtube(url, controller, log_box)

    url_entry = tk.Entry(root, width=60)
    url_entry.pack()

    tk.Button(root, text="Download from Spotify", command=run_spotify).pack()
    tk.Button(root, text="Download from YouTube", command=run_youtube).pack()
    tk.Button(root, text="Pause", command=controller.pause).pack()
    tk.Button(root, text="Resume", command=controller.resume).pack()
    tk.Button(root, text="Cancel", command=controller.cancel).pack()
    tk.Button(root, text="Clean Cache", command=lambda: clean_cache(log_box)).pack()

    root.mainloop()
