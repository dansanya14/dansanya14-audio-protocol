import re

def clean_title(raw_title: str) -> str:
    """
    Remove common junk from titles (e.g. '(Official Video)').
    """
    cleaned = re.sub(r"\(.*?\