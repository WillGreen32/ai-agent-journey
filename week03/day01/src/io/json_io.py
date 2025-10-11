import json
from pathlib import Path

def load_json(path: Path):
    """Load a JSON file into Python."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(path: Path, data):
    """Save JSON with pretty formatting (UTF-8)."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

