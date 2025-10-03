import subprocess, json, os
from gui.logger import log_message

def resolve_youtube_url(search_query: str) -> str:
    result = subprocess.run(
        ["yt-dlp", f"ytsearch1:{search_query}", "--print", "url"],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def check_subtitles(video_url: str) -> str:
    try:
        result = subprocess.run(
            ["yt-dlp", "--list-subs", "--print-json", video_url],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        subs = data.get("subtitles", {})
        auto = data.get("automatic_captions", {})
        if "en" in subs and "en" not in auto:
            return "✅ Owner-uploaded English captions available"
        elif "en" in auto:
            return "⚠️ Only auto-generated captions available"
        else:
            return "❌ No English captions found"
    except Exception:
        return "❌ Subtitle check failed"

def preview_lyrics(flac_path: str) -> str:
    try:
        from mutagen.flac import FLAC
        audio = FLAC(flac_path)
        lyrics = audio.get("LYRICS", "")
        if lyrics:
            lines = lyrics.splitlines()
            return "\n".join(lines[:3]) + "\n..."
        else:
            return "❌ No lyrics embedded"
    except Exception:
        return "❌ Failed to read FLAC metadata"

def debug_track(search_query: str, flac_path: str, log_box=None):
    url = resolve_youtube_url(search_query)
    subtitle_status = check_subtitles(url)
    lyrics_preview = preview_lyrics(flac_path)

    log_message(log_box, f"🔍 Resolved URL: {url}", "INFO")
    log_message(log_box, f"📝 Subtitle Status: {subtitle_status}", "INFO")
    log_message(log_box, f"🎶 Lyrics Preview:\n{lyrics_preview}", "INFO")
