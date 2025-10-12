import csv
from pathlib import Path

def load_csv(path: Path):
    """
    Load a CSV into a list[dict].
    - encoding='utf-8-sig' removes BOM if present
    - newline='' prevents newline translation weirdness
    """
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def save_csv(path: Path, rows, fieldnames):
    """
    Save a list[dict] to CSV with a stable header.
    - newline='' is REQUIRED to avoid extra blank lines on Windows/Excel
    - encoding='utf-8' writes proper Unicode
    """
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
