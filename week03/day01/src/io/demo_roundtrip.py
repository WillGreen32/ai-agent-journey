# src/io/demo_roundtrip.py
# --- Import shim to make it run anywhere ---
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # adds .../day01 to path

from src.io.csv_io import load_csv, save_csv
from src.io.json_io import load_json, save_json
from src.paths import RAW, PROCESSED, ensure_dirs


def normalize_headers(rows):
    """Trim + lowercase all headers and values."""
    cleaned = []
    for row in rows:
        norm = {}
        for k, v in row.items():
            key = (k or "").strip().lower()
            val = (v or "").strip()
            norm[key] = val
        cleaned.append(norm)
    return cleaned


def enforce_schema(rows, fieldnames):
    """Keep only fixed columns and fill missing with blanks."""
    result = []
    for r in rows:
        fixed = {fn: r.get(fn, "") for fn in fieldnames}
        result.append(fixed)
    return result


def main():
    ensure_dirs()

    # --- 1) Seed messy CSV ---
    raw_file = RAW / "customers_roundtrip_source.csv"
    raw_file.write_text(
        " Name , Email , City \n"
        "Will , will@example.com , Melbourne\n"
        "Sarah , sarah@example.com , Sydney\n",
        encoding="utf-8"
    )
    print("Seeded raw file:", raw_file)

    # --- 2) CSV → JSON ---
    rows = load_csv(raw_file)
    cleaned = normalize_headers(rows)
    json_path = PROCESSED / "customers.normalized.json"
    save_json(json_path, cleaned)
    print("Wrote normalized JSON:", json_path)

    # --- 3) JSON → CSV (deterministic order) ---
    fieldnames = ["name", "email", "city"]
    stable = enforce_schema(cleaned, fieldnames)
    csv_path = PROCESSED / "customers.roundtrip.csv"
    save_csv(csv_path, stable, fieldnames)
    print("Wrote roundtrip CSV:", csv_path)

    # --- 4) Verify ---
    again = load_csv(csv_path)
    assert len(again) == 2, f"Row count changed: {len(again)}"
    assert list(again[0].keys()) == fieldnames, "Column order changed!"
    assert again[0]["name"] == "Will", "Data mismatch"

    print("✅ Round-trip succeeded")
    print("JSON:", json_path)
    print("CSV :", csv_path)


if __name__ == "__main__":
    main()
