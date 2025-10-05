import requests
from mutagen.flac import Picture, FLAC
import base64

def extract_video_id(url: str) -> str:
    """Naive extractor for YouTube video ID."""
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    return url.rsplit("/", 1)[-1]

def download_thumbnail(video_id: str):
    """
    Try to fetch the highest resolution thumbnail.
    """
    urls = [
        f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
        f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    ]
    for u in urls:
        r = requests.get(u)
        if r.status_code == 200:
            return r.content
    return None

def embed_thumbnail(file_path: str, image_data: bytes):
    """
    Embed thumbnail into FLAC file as cover art.
    """
    try:
        audio = FLAC(file_path)
        pic = Picture()
        pic.type = 3  # front cover
        pic.mime = "image/jpeg"
        pic.data = image_data
        audio.add_picture(pic)
        audio.save()
    except Exception as e:
        print(f"[WARNING] Failed to embed thumbnail: {e}")
