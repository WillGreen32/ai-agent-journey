import csv
from pathlib import Path

def load_csv(path: Path):
    """Load CSV file into list of dictionaries."""
    with open(path, newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def save_csv(path: Path, data, fieldnames):
    """Save list of dictionaries to CSV file."""
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
