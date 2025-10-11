# labs/csv_basics_lab.py
# (optional) shim so this file also works if you run "python labs\csv_basics_lab.py"
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # adds day01 to sys.path

import csv
from src.paths import RAW, PROCESSED, ensure_dirs


def print_preview(path: Path, label: str):
    """Print first 3 lines so you can eyeball the CSV quickly."""
    print(f"\n{label} -> {path}")
    print("First 3 lines:")
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            print(" ", line.rstrip("\n\r"))
            if i == 2:
                break


def main():
    ensure_dirs()
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)

    # ---------- A) WRITE a clean CSV ----------
    # Notes in 'note' show two tricky cases:
    #  - embedded comma + quotes
    #  - embedded newline inside the cell
    rows = [
        {"name": "Will",  "age": 21, "note": 'Café, "quote" test'},
        {"name": "Sarah", "age": 25, "note": "New\nline inside cell"},
    ]

    csv_out = PROCESSED / "users.clean.csv"
    # newline='' prevents extra blank lines on Windows/Excel.
    # DictWriter handles quoting automatically when needed.
    with open(csv_out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name", "age", "note"])
        w.writeheader()
        w.writerows(rows)
    print_preview(csv_out, "Clean CSV")

    # ---------- B) READ the same CSV ----------
    with open(csv_out, encoding="utf-8") as f:
        r = csv.DictReader(f)  # delimiter defaults to comma
        data = list(r)
        headers = r.fieldnames
    print("\nRead back -> rows:", len(data), "| headers:", headers)
    # prove embedded newline survived round-trip:
    print("Cell with newline? ->", "\\n" in repr(data[1]["note"]))

    # ---------- C) Handle WEIRD CSV (dialect sniffing) ----------
    # Simulate a semicolon-delimited export (common in Europe)
    weird = RAW / "customers_weird.csv"
    weird.write_text(
        "Name;Email;City\r\nWill;will@example.com;Melbourne\r\n",
        encoding="utf-8"
    )

    with open(weird, encoding="utf-8") as f:
        sample = f.read(1024)  # small sample is enough
        f.seek(0)
        # Sniffer detects delimiter, quotechar, etc.
        dialect = csv.Sniffer().sniff(sample)
        r = csv.DictReader(f, dialect=dialect)
        data_weird = list(r)
    print("\nWeird CSV delimiter detected:", repr(dialect.delimiter))
    print("Weird rows:", len(data_weird), "| first row:", data_weird[0])

    # ---------- D) Robust READ with explicit dialect (optional guard) ----------
    # If sniffing fails on some messy files, you can fall back to explicit settings:
    explicit_path = RAW / "customers_weird_explicit.csv"
    explicit_path.write_text(
        "Name;Email;City\nAlice;alice@example.com;Brisbane\n",
        encoding="utf-8"
    )
    with open(explicit_path, encoding="utf-8", newline="") as f:
        r = csv.DictReader(f, delimiter=";", quotechar='"')
        data_explicit = list(r)
    print("\nExplicit read -> rows:", len(data_explicit), "| headers:", r.fieldnames)


if __name__ == "__main__":
    main()
    print("\n✅ CSV basics lab complete.")
