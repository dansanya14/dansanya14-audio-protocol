import subprocess
import re
import json
from downloader.retry import retry

YOUTUBE_URL_RE = re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/")


def is_youtube_url(text: str) -> bool:
    return bool(YOUTUBE_URL_RE.search(text))


def is_playlist_url(url: str) -> bool:
    return "list=" in url or "playlist" in url


def resolve_youtube_url(query_or_url, logger):
    """Resolve a search query or URL into a usable YouTube URL."""
    if is_youtube_url(query_or_url):
        if "shorts" in query_or_url:
            logger.log_message(f"Skipping Shorts URL: {query_or_url}", "WARNING")
            return None
        return query_or_url

    def _resolve():
        return subprocess.run(
            ["yt-dlp", f"ytsearch1:{query_or_url}", "--print", "url"],
            capture_output=True, text=True, check=True
        ).stdout.strip()

    url = retry(
        action=_resolve,
        description=f"Resolving YouTube URL for {query_or_url}",
        logger=logger,
        retries=3,
        base_delay=2,
        min_interval=1.5
    )
    if not url:
        logger.log_message(f"Could not resolve YouTube input: {query_or_url}", "ERROR")
    return url


def is_channel_url(url: str) -> bool:
    return any(x in url for x in ["/channel/", "/c/", "/@", "youtube.com/user/"])


def get_channel_items(url, logger):
    """Return a list of video URLs from a channel, skipping Shorts."""
    def _extract():
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "-J", url],
            capture_output=True, text=True, check=True
        )
        return json.loads(result.stdout)

    data = retry(
        action=_extract,
        description=f"Fetching channel items for {url}",
        logger=logger,
        retries=3,
        base_delay=2,
        min_interval=2.0
    )
    if not data:
        return []

    entries = data.get("entries", [])
    urls = []
    for e in entries:
        if "id" in e:
            vid_url = f"https://www.youtube.com/watch?v={e['id']}"
            # Filter out Shorts
            if "/shorts/" not in vid_url and "shorts" not in e.get("title", "").lower():
                urls.append(vid_url)
    return urls


def get_playlist_items(url, logger):
    """Return a list of video URLs in a playlist using yt-dlp --flat-playlist."""
    def _extract():
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "-J", url],
            capture_output=True, text=True, check=True
        )
        return json.loads(result.stdout)

    data = retry(
        action=_extract,
        description=f"Fetching playlist items for {url}",
        logger=logger,
        retries=3,
        base_delay=2,
        min_interval=2.0
    )
    if not data:
        return []

    entries = data.get("entries", [])
    return [f"https://www.youtube.com/watch?v={e['id']}" for e in entries if "id" in e]


def download_audio(url, output_template, logger):
    """Download audio as FLAC using yt-dlp. Returns True on success, None on failure."""
    command = ["yt-dlp", url, "-x", "--audio-format", "flac", "-o", output_template]

    def _download():
        subprocess.run(command, check=True)
        return True  # explicit success

    return retry(
        action=_download,
        description=f"Downloading {url}",
        logger=logger,
        retries=3,
        base_delay=3,
        min_interval=2.0
    )
