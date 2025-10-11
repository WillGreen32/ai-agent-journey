# src/io/write_csv_from_json.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.paths import PROCESSED
from src.io.json_io import load_json
from src.io.csv_io import save_csv

def main():
    schema = ["name", "email", "city"]  # locked order
    data = load_json(PROCESSED / "customers.cleaned.json")
    csv_out = PROCESSED / "customers.cleaned.csv"
    save_csv(csv_out, data, schema)
    print("Wrote CSV:", csv_out)

if __name__ == "__main__":
    main()
