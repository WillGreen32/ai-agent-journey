import sys
import json
import csv
from pathlib import Path
# add project root (day01) so 'src' is importable when run as a script
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# labs/encodings_bom_lab.py
from pathlib import Path
import json, csv

# Use your anchor constants so paths are ALWAYS correct
from src.paths import RAW, PROCESSED, ensure_dirs

def show_bytes_head(path: Path, n=8):
    b = path.read_bytes()[:n]
    print(f"  first {n} bytes:", " ".join(f"{x:02X}" for x in b))

def main():
    ensure_dirs()
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)

    # ---------- Part 1: Plain text encodings ----------
    print("\nPART 1: Plain text encodings")

    txt_utf8   = PROCESSED / "utf8_no_bom.txt"
    txt_utf8_sig = PROCESSED / "utf8_with_bom.txt"

    content = "Name, City\nCafé, Melbourne\nNaïve, Sydney\nEmoji: 😀\n"

    # A) Write UTF-8 (no BOM)
    txt_utf8.write_text(content, encoding="utf-8")
    print(f"wrote: {txt_utf8} (utf-8)")
    show_bytes_head(txt_utf8)

    # B) Write UTF-8 with BOM
    txt_utf8_sig.write_text(content, encoding="utf-8-sig")
    print(f"wrote: {txt_utf8_sig} (utf-8-sig, adds BOM)")
    show_bytes_head(txt_utf8_sig)
    print("  tip: BOM bytes for UTF-8 are EF BB BF")

    # Read both back with different encodings
    print("\nRead back with different encodings:")
    a = txt_utf8.read_text(encoding="utf-8")
    b = txt_utf8_sig.read_text(encoding="utf-8")      # <- shows \\ufeff at start
    c = txt_utf8_sig.read_text(encoding="utf-8-sig")  # <- BOM removed automatically
    print("  utf8_no_bom read as utf-8 -> OK, starts with:", repr(a.splitlines()[0]))
    print("  utf8_with_bom read as utf-8 -> shows BOM:", repr(b.splitlines()[0]))
    print("  utf8_with_bom read as utf-8-sig -> clean:", repr(c.splitlines()[0]))

   # ---------- Part 2: CSV with BOM ----------
print("\nPART 2: CSV with BOM")

customers_bom = RAW / "customers_bom.csv"
rows = [
    {"Name": "Will",  "Email": "will@example.com",  "City": "Melbourne"},
    {"Name": "Sarah", "Email": "sarah@example.com", "City": "Sydney"},
]

# Write CSV WITH BOM (utf-8-sig) to simulate messy export
with open(customers_bom, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["Name", "Email", "City"])
    writer.writeheader()
    writer.writerows(rows)
print(f"wrote: {customers_bom} (utf-8-sig)")
show_bytes_head(customers_bom)

# Try to read the "messy" file two ways:
with open(customers_bom, encoding="utf-8") as f:
    r = csv.DictReader(f)
    headers = r.fieldnames
print("  read with utf-8 -> headers:", headers, "(notice BOM sticks to first header)")

with open(customers_bom, encoding="utf-8-sig") as f:
    r = csv.DictReader(f)
    headers = r.fieldnames
print("  read with utf-8-sig -> headers:", headers, "(clean)")


if __name__ == "__main__":
    main()
    print("\n✅ Encodings & BOM lab complete.")
