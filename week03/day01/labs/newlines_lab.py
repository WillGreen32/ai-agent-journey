import sys
from pathlib import Path
# add project root (day01) so 'src' is importable when run as a script
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# labs/newlines_lab.py
from pathlib import Path
import csv, os
from src.paths import PROCESSED, ensure_dirs

def show_bytes_preview(path: Path, n=40):
    b = path.read_bytes()[:n]
    print(f"  first {n} bytes:", " ".join(f"{x:02X}" for x in b))

def main():
    ensure_dirs()

    rows = [{"name": "Will"}, {"name": "Sarah"}]

    bad = PROCESSED / "bad_newlines.csv"
    good = PROCESSED / "good_newlines.csv"

    # BAD: omit newline='' (causes extra blank lines on Windows/Excel)
    with open(bad, "w", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name"])
        w.writeheader()
        w.writerows(rows)
    print("wrote:", bad)
    show_bytes_preview(bad)

    # GOOD: newline='' lets csv module control newlines correctly
    with open(good, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name"])
        w.writeheader()
        w.writerows(rows)
    print("wrote:", good)
    show_bytes_preview(good)

    # Count logical rows both ways
    def count_lines(p: Path):
        return sum(1 for _ in p.open(encoding="utf-8"))

    print("\nlogical lines (reading text):")
    print("  bad_newlines.csv:", count_lines(bad))
    print("  good_newlines.csv:", count_lines(good))

    print("\nos info:")
    print("  os.name:", os.name, " (nt=Windows, posix=Mac/Linux)")
    print("  writing CSV? -> always use newline='' for portability")

if __name__ == "__main__":
    main()
    print("\n✅ Newlines lab complete.")
