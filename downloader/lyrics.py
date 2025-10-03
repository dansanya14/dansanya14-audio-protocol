# Handles embedding lyrics from YouTube captions

from mutagen.flac import FLAC
from gui.logger import log_message
import os, re

def extract_clean_captions(srt_path: str) -> str:
    if not os.path.exists(srt_path):
        return ""
    with open(srt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    text_lines = []
    for line in lines:
        line = line.strip()
        if re.match(r"^\d+$", line): continue
        if re.match(r"^\d{2}:\d{2}:\d{2},\d{3}", line): continue
        if line: text_lines.append(line)
    return "\n".join(text_lines)

def fetch_lyrics(title: str, artist: str, file_path: str, log_box=None):
    try:
        srt_path = file_path.replace(".flac", ".en.srt")
        lyrics = extract_clean_captions(srt_path)
        if lyrics:
            audio = FLAC(file_path)
            audio["LYRICS"] = f"[Source: YouTube captions]\n\n{lyrics}"
            audio.save()
            log_message(log_box, f"Lyrics embedded from YouTube captions for {title}", "SUCCESS")
        else:
            log_message(log_box, f"No usable captions found for {title}", "WARNING")
    except Exception as e:
        log_message(log_box, f"Lyrics embedding failed: {e}", "ERROR")
