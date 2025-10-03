from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from downloader.retry import retry
from downloader.metadata import tag_audio
from gui.logger import log_message
from config import DOWNLOAD_DIR
from mutagen.flac import FLAC
from downloader.thumbnails import extract_video_id, download_thumbnail, embed_thumbnail
import subprocess, os, shutil, time, json, re, glob

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

def find_latest_flac():
    files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.flac"))
    return max(files, key=os.path.getctime) if files else None

def clean_title(raw: str) -> str:
    cleaned = re.sub(r"

    \[.*?\]

    |\(.*?\)", "", raw)
    cleaned = re.sub(r"\b(official|video|lyrics|HD|4K|remastered)\b", "", cleaned, flags=re.IGNORECASE)
    return " ".join(cleaned.split()).strip()

def download_spotify(playlist_url: str, controller, log_box=None):
    log_message(log_box, "Starting Spotify download...", "INFO")
    try:
        tracks = get_spotify_tracks(playlist_url)
    except Exception as e:
        log_message(log_box, f"Failed to fetch playlist: {e}", "ERROR")
        return

    ffmpeg_location = get_ffmpeg_location()
    total_tracks = len(tracks)

    for index, track in enumerate(tracks):
        if not controller.should_continue():
            log_message(log_box, "Download cancelled.", "WARNING")
            break
        while controller.paused:
            log_message(log_box, "Paused...", "INFO")
            time.sleep(1)

        search_query = f"{track['artist']} - {track['title']}"
        output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

        # Resolve actual video URL
        resolved_url = subprocess.run(
            ["yt-dlp", f"ytsearch1:{search_query}", "--print", "url"],
            capture_output=True, text=True
        ).stdout.strip()

        if not resolved_url or "youtube.com" not in resolved_url:
            log_message(log_box, f"No YouTube match found for {search_query}. Skipping track.", "WARNING")
            continue

        log_message(log_box, f"Resolved YouTube URL: {resolved_url}", "INFO")

        def action():
            command = [
                "yt-dlp", resolved_url,
                "-x", "--audio-format", "flac",
                "-o", output_template
            ]
            if ffmpeg_location:
                command += ["--ffmpeg-location", ffmpeg_location]

            if has_manual_subs(resolved_url, lang="en"):
                command += ["--write-subs", "--sub-langs", "en", "--convert-subs", "srt"]
                log_message(log_box, f"Captions found for {search_query}. Downloading subtitles...", "INFO")
            else:
                log_message(log_box, f"No owner-uploaded captions for {search_query}. Skipping subtitles.", "INFO")

            subprocess.run(command, check=True)

        if retry(action, f"Download {search_query}", log_box):
            flac_file = find_latest_flac()
            if flac_file:
                # Embed thumbnail
                video_id = extract_video_id(resolved_url)
                image_data = download_thumbnail(video_id)
                if image_data:
                    embed_thumbnail(flac_file, image_data)
                    log_message(log_box, f"Thumbnail embedded for {track['title']}", "SUCCESS")
                else:
                    log_message(log_box, f"No thumbnail found for {track['title']}", "WARNING")

                # Clean title and tag metadata
                cleaned_title = clean_title(track["title"])
                tag_audio(flac_file, {
                    "title": cleaned_title,
                    "artist": track["artist"],
                    "album": track["album"]
                })

                # Embed lyrics
                srt_path = flac_file.replace(".flac", ".en.srt")
                lyrics = extract_clean_captions(srt_path)
                if lyrics:
                    audio = FLAC(flac_file)
                    audio["LYRICS"] = f"[Source: YouTube captions]\n\n{lyrics}"
                    audio.save()
                    log_message(log_box, f"Lyrics embedded from YouTube captions for {track['title']}", "SUCCESS")
                else:
                    log_message(log_box, f"No usable captions found for {track['title']}", "WARNING")

                controller.update_progress((index + 1) / total_tracks)
            else:
                log_message(log_box, "Download complete, but FLAC file not found.", "WARNING")
