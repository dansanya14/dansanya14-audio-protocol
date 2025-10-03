# downloader/metadata.py

from mutagen.flac import FLAC
from gui.logger import log_message

def tag_audio(file_path: str, metadata: dict, log_box=None):
    try:
        audio = FLAC(file_path)
        audio["title"] = metadata.get("title", "")
        audio["artist"] = metadata.get("artist", "")
        audio["album"] = metadata.get("album", "")
        audio.save()
        log_message(log_box, f"Tagged: {metadata['title']} by {metadata['artist']}", "SUCCESS")
    except Exception as e:
        log_message(log_box, f"Metadata tagging failed: {e}", "ERROR")
