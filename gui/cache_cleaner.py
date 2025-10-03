import os
import shutil
from config import CACHE_DIR
from gui.logger import log_message

def clean_cache(log_box=None):
    try:
        shutil.rmtree(CACHE_DIR)
        os.makedirs(CACHE_DIR)
        log_message(log_box, "Cache cleaned.", "SUCCESS")
    except Exception as e:
        log_message(log_box, f"Cache clean failed: {e}", "ERROR")
