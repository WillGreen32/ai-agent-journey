# src/io/demo_pipeline.py
# --- Shim so it runs as module OR as a script ---
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # adds .../day01 to sys.path

from src.paths import RAW, PROCESSED, ensure_dirs
from .csv_io import load_csv, save_csv
from .json_io import save_json  # load_json not needed here

# 🔒 Explicit, locked schema (deterministic column order everywhere)
SCHEMA = ["name", "email", "city"]


def _normalize_rows(rows: list[dict]) -> list[dict]:
    """
    Normalize headers and values:
    - headers: strip + lowercase; drop empty header names
    - values : strip; keep None-safe
    """
    cleaned: list[dict] = []
    for row in rows:
        out = {}
        for k, v in row.items():
            key = (k or "").strip().lower()
            if not key:
                continue
            out[key] = (v or "").strip()
        cleaned.append(out)
    return cleaned


def _enforce_schema(rows: list[dict], fieldnames: list[str]) -> list[dict]:
    """Keep only SCHEMA columns and insert any missing ones as empty strings."""
    return [{k: r.get(k, "") for k in fieldnames} for r in rows]


def main():
    ensure_dirs()

    raw = RAW / "customers.csv"
    json_out = PROCESSED / "customers.json"
    csv_out = PROCESSED / "customers_roundtrip.csv"

    # --- Guard: input must exist
    if not raw.exists():
        raise FileNotFoundError(
            f"Missing input file: {raw}\n"
            "Create it at data/raw/customers.csv (e.g.):\n"
            "Name , Email , City\nWill , will@example.com , Melbourne\nSarah , sarah@example.com , Sydney\n"
        )

    # --- Step 1: Ingest (friendly error handling)
    try:
        rows = load_csv(raw)
    except Exception as e:
        print(f"❌ Failed to read CSV: {e!r}")
        return

    if not rows:
        print("⚠️  Input CSV is empty. Nothing to do.")
        return

    # --- Step 2: Normalize
    cleaned = _normalize_rows(rows)

    # --- 🔒 Enforce schema (this replaces any _stable_fieldnames logic)
    stable = _enforce_schema(cleaned, SCHEMA)

    # --- Step 3: Write JSON (pretty UTF-8)
    try:
        save_json(json_out, stable)
    except Exception as e:
        print(f"❌ Failed to write JSON: {e!r}")
        return

    # --- Step 4: Write CSV (deterministic header order)
    try:
        save_csv(csv_out, stable, SCHEMA)
    except Exception as e:
        print(f"❌ Failed to write CSV: {e!r}")
        return

    # --- Tiny summary
    cities = sorted({r.get("city", "") for r in stable if r.get("city")})
    print(f"Rows: {len(stable)} | Cities: {', '.join(cities) if cities else '(none)'}")

    print("✅ Pipeline complete!")
    print("JSON:", json_out)
    print("CSV :", csv_out)


if __name__ == "__main__":
    main()
