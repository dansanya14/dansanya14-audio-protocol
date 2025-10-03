# Manages the YouTube download

import subprocess, os, shutil, glob, json, re
from downloader.retry import retry
from downloader.metadata import tag_audio
from gui.logger import log_message
from config import DOWNLOAD_DIR
from mutagen.flac import FLAC

def get_ffmpeg_location():
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        return None
    local_bin = os.path.join("ffmpeg", "ffmpeg-8.0-essentials_build", "bin")
    if os.path.exists(os.path.join(local_bin, "ffmpeg.exe")) and os.path.exists(os.path.join(local_bin, "ffprobe.exe")):
        return local_bin
    return None

def has_manual_subs(video_url: str, lang="en") -> bool:
    try:
        result = subprocess.run(
            ["yt-dlp", "--list-subs", "--print-json", video_url],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        subs = data.get("subtitles", {})
        auto_subs = data.get("automatic_captions", {})
        return lang in subs and lang not in auto_subs
    except Exception:
        return False

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

def infer_title_artist(filename: str):
    base = os.path.splitext(os.path.basename(filename))[0]
    if " - " in base:
        artist, title = base.split(" - ", 1)
    else:
        artist, title = "Unknown", base
    return title.strip(), artist.strip()

def find_latest_flac():
    files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.flac"))
    return max(files, key=os.path.getctime) if files else None

def download_youtube(video_url: str, controller, log_box=None):
    log_message(log_box, "Starting YouTube download...", "INFO")

    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ffmpeg_location = get_ffmpeg_location()

    def action():
        command = [
            "yt-dlp", video_url,
            "-x", "--audio-format", "flac",
            "-o", output_path
        ]
        if ffmpeg_location:
            command += ["--ffmpeg-location", ffmpeg_location]

        if has_manual_subs(video_url, lang="en"):
            command += ["--write-subs", "--sub-langs", "en", "--convert-subs", "srt"]
            log_message(log_box, "Owner-uploaded captions detected. Capturing subtitles...", "INFO")
        else:
            log_message(log_box, "No owner-uploaded captions found. Skipping subtitles.", "INFO")

        subprocess.run(command, check=True)

    if retry(action, f"Download {video_url}", log_box):
        flac_file = find_latest_flac()
        if flac_file:
            title, artist = infer_title_artist(flac_file)
            tag_audio(flac_file, {"title": title, "artist": artist, "album": "YouTube"})

            srt_path = flac_file.replace(".flac", ".en.srt")
            lyrics = extract_clean_captions(srt_path)
            if lyrics:
                audio = FLAC(flac_file)
                audio["LYRICS"] = f"[Source: YouTube captions]\n\n{lyrics}"
                audio.save()
                log_message(log_box, f"Lyrics embedded from YouTube captions for {title}", "SUCCESS")
            else:
                log_message(log_box, f"No usable captions found for {title}", "WARNING")
        else:
            log_message(log_box, "Download complete, but FLAC file not found.", "WARNING")
