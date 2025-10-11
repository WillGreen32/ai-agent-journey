# src/io/ingest_normalize_write.py
# Import shim so this runs as a module OR direct script
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # adds .../day01 to sys.path

from typing import List, Dict
from src.paths import RAW, PROCESSED, ensure_dirs
from src.io.csv_io import load_csv, save_csv
from src.io.json_io import load_json, save_json


# ---------- 1) Ingest ----------
def ingest_csv(path: Path) -> List[Dict[str, str]]:
    """
    Read CSV as list of dicts using utf-8-sig (BOM-safe).
    Empty files yield [].
    """
    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")
    rows = load_csv(path)  # our loader uses encoding='utf-8-sig', newline=''
    return rows


# ---------- 2) Normalize ----------
def normalize_headers(rows: List[Dict[str, str]], mapping: Dict[str, str] | None = None) -> List[Dict[str, str]]:
    """
    - Trim spaces around header names
    - Lowercase header names
    - Apply optional synonym mapping (e.g., 'e-mail' -> 'email')
    - Drop columns with empty header names
    """
    mapping = { (k.strip().lower()): v.strip().lower() for k, v in (mapping or {}).items() }

    cleaned: List[Dict[str, str]] = []
    for row in rows:
        out: Dict[str, str] = {}
        for k, v in row.items():
            key = (k or "").strip().lower()
            if not key:
                continue  # drop columns with no header
            key = mapping.get(key, key)  # apply synonyms if provided
            out[key] = (v or "").strip()
        cleaned.append(out)
    return cleaned


def normalize_values(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Row-level value cleanup:
    - Trim whitespace
    - Collapse internal runs of whitespace to single spaces
    - Lowercase email if present
    """
    cleaned: List[Dict[str, str]] = []
    for r in rows:
        out = {}
        for k, v in r.items():
            val = (v or "").strip()
            # collapse multiple spaces -> single
            val = " ".join(val.split())
            if k == "email":
                val = val.lower()
            out[k] = val
        cleaned.append(out)
    return cleaned


def enforce_schema(rows: List[Dict[str, str]], fieldnames: list[str]) -> List[Dict[str, str]]:
    """
    Guarantee deterministic column set & order.
    - Keep only columns in 'fieldnames'
    - Insert missing columns as empty strings
    """
    result: List[Dict[str, str]] = []
    for r in rows:
        result.append({fn: r.get(fn, "") for fn in fieldnames})
    return result


# ---------- 3) Write ----------
def write_json(path: Path, data) -> None:
    """Wrapper so everything writes with UTF-8 & indentation."""
    save_json(path, data)


# ---------- 4) Orchestrator ----------
def run_pipeline(
    input_csv: Path,
    json_out: Path,
    fieldnames: list[str] = None,
    header_map: Dict[str, str] | None = None,
) -> None:
    """
    Ingest -> Normalize -> Write
    - fieldnames: final schema (ordered)
    - header_map: optional column synonyms to map during normalization
    """
    ensure_dirs()

    print(f"📥 Ingest: {input_csv}")
    raw_rows = ingest_csv(input_csv)
    print(f"  rows read: {len(raw_rows)}")

    print("🧼 Normalize: headers & values")
    rows = normalize_headers(raw_rows, mapping=header_map)
    rows = normalize_values(rows)

    if fieldnames:
        print(f"🧩 Enforce schema: {fieldnames}")
        rows = enforce_schema(rows, fieldnames)

    print(f"💾 Write JSON: {json_out}")
    write_json(json_out, rows)

    # Mini-report
    if rows:
        print("  sample row:", rows[0])
    print("✅ Done")


def main():
    ensure_dirs()

    # Create a messy seed CSV if it doesn't exist (makes the lab repeatable)
    seed = RAW / "customers_ingest.csv"
    if not seed.exists():
        seed.write_text(
            " Name , E-mail , City \n"
            "Will  , Will@Example.com ,  Melbourne \n"
            "Sarah ,  sarah@example.com, Sydney   \n",
            encoding="utf-8"
        )

    # Define canonical schema (column order) + header synonyms
    schema = ["name", "email", "city"]
    synonyms = {"e-mail": "email", "email address": "email"}

    json_out = PROCESSED / "customers.cleaned.json"
    run_pipeline(
        input_csv=seed,
        json_out=json_out,
        fieldnames=schema,
        header_map=synonyms,
    )


if __name__ == "__main__":
    main()
