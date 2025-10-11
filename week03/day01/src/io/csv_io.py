import csv
from pathlib import Path

def load_csv(path: Path):
    """Load CSV safely with utf-8-sig and return list of dicts."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_csv(path: Path, rows, fieldnames):
    """Write CSV with consistent quoting and newline handling."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
