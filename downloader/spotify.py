# Manages the Spotify download

from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from downloader.retry import retry
from downloader.metadata import tag_audio
from gui.logger import log_message
from config import DOWNLOAD_DIR
from mutagen.flac import FLAC
import subprocess, os, shutil, time, json, re

# Replace with your actual credentials or use fallback logic
SPOTIFY_CLIENT_ID = "your-client-id"
SPOTIFY_CLIENT_SECRET = "your-client-secret"

def get_spotify_tracks(playlist_url: str) -> list:
    sp = Spotify(auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    ))
    playlist_id = playlist_url.split("/")[-1].split("?")[0]
    results = sp.playlist_tracks(playlist_id)
    tracks = []
    for item in results["items"]:
        track = item["track"]
        tracks.append({
            "title": track["name"],
            "artist": track["artists"][0]["name"],
            "album": track["album"]["name"],
            "url": f"{track['external_urls']['spotify']}"
        })
    return tracks

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

def download_spotify(playlist_url: str, controller, log_box=None):
    log_message(log_box, "Starting Spotify download...", "INFO")
    try:
        tracks = get_spotify_tracks(playlist_url)
    except Exception as e:
        log_message(log_box, f"Failed to fetch playlist: {e}", "ERROR")
        return

    ffmpeg_location = get_ffmpeg_location()

    for track in tracks:
        if not controller.should_continue():
            log_message(log_box, "Download cancelled.", "WARNING")
            break
        while controller.paused:
            log_message(log_box, "Paused...", "INFO")
            time.sleep(1)

        search_query = f"{track['artist']} - {track['title']}"
        output_path = os.path.join(DOWNLOAD_DIR, f"{track['title']}.flac")

        def action():
            command = [
                "yt-dlp", f"ytsearch1:{search_query}",
                "-x", "--audio-format", "flac",
                "-o", output_path
            ]
            if ffmpeg_location:
                command += ["--ffmpeg-location", ffmpeg_location]

            # Check if owner-uploaded captions exist
            if has_manual_subs(f"ytsearch1:{search_query}", lang="en"):
                command += ["--write-subs", "--sub-langs", "en", "--convert-subs", "srt"]
                log_message(log_box, f"Captions found for {search_query}. Downloading subtitles...", "INFO")
            else:
                log_message(log_box, f"No owner-uploaded captions for {search_query}. Skipping subtitles.", "INFO")

            subprocess.run(command, check=True)

        if retry(action, f"Download {search_query}", log_box):
            tag_audio(output_path, track)

            srt_path = output_path.replace(".flac", ".en.srt")
            lyrics = extract_clean_captions(srt_path)
            if lyrics:
                audio = FLAC(output_path)
                audio["LYRICS"] = f"[Source: YouTube captions]\n\n{lyrics}"
                audio.save()
                log_message(log_box, f"Lyrics embedded from YouTube captions for {track['title']}", "SUCCESS")
            else:
                log_message(log_box, f"No usable captions found for {track['title']}", "WARNING")
