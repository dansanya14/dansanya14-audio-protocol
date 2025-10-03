# downloader/thumbnails.py

import requests
from mutagen.flac import FLAC, Picture
import base64

def extract_video_id(url: str) -> str:
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    return url.split("/")[-1]

def download_thumbnail(video_id: str) -> bytes | None:
    url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    return None

def embed_thumbnail(flac_path: str, image_data: bytes):
    audio = FLAC(flac_path)
    pic = Picture()
    pic.data = image_data
    pic.type = 3  # Cover (front)
    pic.mime = "image/jpeg"
    pic.width = 1280
    pic.height = 720
    pic.depth = 24
    audio["metadata_block_picture"] = [base64.b64encode(pic.write()).decode("utf-8")]
    audio.save()
