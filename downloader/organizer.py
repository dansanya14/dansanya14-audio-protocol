# downloader/organizer.py

import os
import shutil
from config import DOWNLOAD_DIR
from gui.logger import log_message

def move_to_library(file_path: str, artist: str, log_box=None):
    try:
        artist_folder = os.path.join(DOWNLOAD_DIR, artist)
        os.makedirs(artist_folder, exist_ok=True)
        dest = os.path.join(artist_folder, os.path.basename(file_path))
        shutil.move(file_path, dest)
        log_message(log_box, f"Moved to library: {dest}", "SUCCESS")
    except Exception as e:
        log_message(log_box, f"Move failed: {e}", "ERROR")

def clean_temp_files(temp_dir: str, log_box=None):
    try:
        for root, _, files in os.walk(temp_dir):
            for f in files:
                os.remove(os.path.join(root, f))
        log_message(log_box, "Temporary files cleaned.", "SUCCESS")
    except Exception as e:
        log_message(log_box, f"Temp cleanup failed: {e}", "ERROR")
