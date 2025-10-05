import os

def file_exists(track, return_path=False, base_dir="downloads"):
    """
    Check if a FLAC file for this track already exists in base_dir.
    """
    filename = f"{track['title']}.flac"
    path = os.path.join(base_dir, filename)
    if os.path.exists(path):
        return path if return_path else True
    return None if return_path else False
