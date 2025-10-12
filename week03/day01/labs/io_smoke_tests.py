# labs/io_smoke_tests.py
# Add project root (day01) to sys.path so 'src' is importable if run as a script
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.paths import PROCESSED, ensure_dirs
from src.io.json_io import save_json, load_json
from src.io.csv_io import save_csv, load_csv

def main():
    ensure_dirs()
    PROCESSED.mkdir(parents=True, exist_ok=True)

    # ----- JSON test -----
    jpath = PROCESSED / "smoke.json"
    payload = {"ok": True, "note": "Café 😀"}
    save_json(jpath, payload)
    obj = load_json(jpath)
    print("JSON ok:", obj == payload)

    # ----- CSV test -----
    cpath = PROCESSED / "smoke.csv"
    rows = [{"name": "A"}, {"name": "B"}]
    save_csv(cpath, rows, fieldnames=["name"])
    back = load_csv(cpath)
    print("CSV ok:", back == rows)

if __name__ == "__main__":
    main()
