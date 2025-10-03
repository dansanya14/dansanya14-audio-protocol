from downloader.retry import retry
from downloader.metadata import tag_audio
from downloader.lyrics import extract_clean_captions
from downloader.thumbnails import extract_video_id, download_thumbnail, embed_thumbnail
from gui.logger import log_message
from config import DOWNLOAD_DIR
from mutagen.flac import FLAC
import subprocess, os, shutil, time, json, re, glob

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

def find_latest_flac():
    files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.flac"))
    return max(files, key=os.path.getctime) if files else None

def clean_title(raw: str) -> str:
    cleaned = re.sub(r"

    \[.*?\]

    |\(.*?\)", "", raw)
    cleaned = re.sub(r"\b(official|video|lyrics|HD|4K|remastered)\b", "", cleaned, flags=re.IGNORECASE)
    return " ".join(cleaned.split()).strip()

def download_youtube(video_urls: list[str], controller, log_box=None):
    log_message(log_box, "Starting batch YouTube download...", "INFO")
    ffmpeg_location = get_ffmpeg_location()
    output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    total = len(video_urls)

    for index, video_url in enumerate(video_urls):
        if not controller.should_continue():
            log_message(log_box, "Batch cancelled.", "WARNING")
            break
        while controller.paused:
            log_message(log_box, "Paused...", "INFO")
            time.sleep(1)

        log_message(log_box, f"Downloading {video_url} ({index+1}/{total})", "INFO")

        def action():
            command = [
                "yt-dlp", video_url,
                "-x", "--audio-format", "flac",
                "-o", output_template
            ]
            if ffmpeg_location:
                command += ["--ffmpeg-location", ffmpeg_location]

            if has_manual_subs(video_url, lang="en"):
                command += ["--write-subs", "--sub-langs", "en", "--convert-subs", "srt"]
                log_message(log_box, "Captions found. Downloading subtitles...", "INFO")
            else:
                log_message(log_box, "No owner-uploaded captions. Skipping subtitles.", "INFO")

            subprocess.run(command, check=True)

        if retry(action, f"Download {video_url}", log_box):
            flac_path = find_latest_flac()
            if flac_path:
                # Embed thumbnail
                video_id = extract_video_id(video_url)
                image_data = download_thumbnail(video_id)
                if image_data:
                    embed_thumbnail(flac_path, image_data)
                    log_message(log_box, "Thumbnail embedded.", "SUCCESS")
                else:
                    log_message(log_box, "No thumbnail found.", "WARNING")

                # Clean title and tag metadata
                raw_title = os.path.splitext(os.path.basename(flac_path))[0]
                cleaned_title = clean_title(raw_title)
                tag_audio(flac_path, {
                    "title": cleaned_title,
                    "artist": "YouTube",
                    "album": "YouTube Downloads"
                })

                # Embed lyrics
                srt_path = flac_path.replace(".flac", ".en.srt")
                lyrics = extract_clean_captions(srt_path)
                if lyrics:
                    audio = FLAC(flac_path)
                    audio["LYRICS"] = f"[Source: YouTube captions]\n\n{lyrics}"
                    audio.save()
                    log_message(log_box, "Lyrics embedded from YouTube captions.", "SUCCESS")
                else:
                    log_message(log_box, "No usable captions found.", "WARNING")

                controller.update_progress((index + 1) / total)
            else:
                log_message(log_box, "Download complete, but FLAC file not found.", "WARNING")
