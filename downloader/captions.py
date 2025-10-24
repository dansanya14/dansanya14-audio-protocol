import os

def has_manual_subs(url: str, lang="en") -> bool:
    """
    Placeholder: always return False for now.
    Later: use yt-dlp to check for manual subtitles.
    """
    return False

def extract_clean_captions(srt_path: str) -> str:
    """
    Placeholder: read .srt file and return plain text.
    """
    if not os.path.exists(srt_path):
        return None
    with open(srt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    # Strip numbers and timestamps
    text = [line.strip() for line in lines if not line.strip().isdigit() and "-->" not in line]
    return "\n".join(text)

def embed_captions(file_path: str, text: str):
    """
    Placeholder: embed captions as a FLAC tag (LYRICS).
    """
    try:
        from mutagen.flac import FLAC
        audio = FLAC(file_path)
        audio["LYRICS"] = text
        audio.save()
    except Exception as e:
        print(f"[WARNING] Failed to embed captions: {e}")
