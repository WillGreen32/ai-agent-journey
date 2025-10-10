from io.csv_io import load_csv, save_csv
from io.json_io import load_json, save_json
from week03.day01.src.paths import RAW, PROCESSED, ensure_dirs
from pathlib import Path

def main():
    ensure_dirs()
    raw_file = RAW / "customers.csv"
    json_out = PROCESSED / "customers.json"
    csv_out = PROCESSED / "customers_roundtrip.csv"

    # Step 1 — Ingest CSV
    rows = load_csv(raw_file)

    # Step 2 — Normalize headers & values
    cleaned = [{k.strip().lower(): v.strip() for k, v in row.items()} for row in rows]

    # Step 3 — Save to JSON
    save_json(json_out, cleaned)

    # Step 4 — Round-trip JSON → CSV
    fieldnames = list(cleaned[0].keys())
    save_csv(csv_out, cleaned, fieldnames)

    print("✅ Pipeline complete!")

if __name__ == "__main__":
    main()
