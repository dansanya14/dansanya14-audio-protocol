import csv

def parse_exportify_csv(file_path):
    """
    Parse an Exportify CSV file into a list of track dicts.
    """
    tracks = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            track = {
                "title": row.get("Track Name", "").strip(),
                "artist": row.get("Artist Name", "").strip(),
                "album": row.get("Album Name", "").strip(),
                "url": None
            }
            if track["title"] and track["artist"]:
                tracks.append(track)
    return tracks
