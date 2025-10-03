import os, glob
from config import DOWNLOAD_DIR

def clean_cache():
    extensions = [".part", ".temp", ".webm", ".info.json"]
    removed = 0
    for ext in extensions:
        for f in glob.glob(os.path.join(DOWNLOAD_DIR, f"*{ext}")):
            try:
                os.remove(f)
                removed += 1
            except Exception:
                pass
    return removed
