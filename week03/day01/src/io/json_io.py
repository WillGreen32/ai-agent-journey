import json
from pathlib import Path

def load_json(path: Path):
    """Load JSON file into Python object."""
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def save_json(path: Path, data):
    """Save Python object to JSON file with nice formatting."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
