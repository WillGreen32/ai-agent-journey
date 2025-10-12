import json
from pathlib import Path

def load_json(path: Path):
    """Load JSON into a Python object."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(path: Path, data):
    """
    Save JSON with pretty indentation and Unicode preserved.
    - ensure_ascii=False keeps real characters (é, 😀) instead of \\u escapes
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

