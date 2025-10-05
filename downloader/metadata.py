from mutagen.flac import FLAC

def tag_audio(file_path: str, tags: dict):
    """
    Embed basic metadata into a FLAC file.
    tags = {"title": ..., "artist": ..., "album": ...}
    """
    try:
        audio = FLAC(file_path)
        for key, value in tags.items():
            audio[key] = value
        audio.save()
    except Exception as e:
        print(f"[WARNING] Failed to tag {file_path}: {e}")
