from pathlib import Path

# ROOT = .../week03/day01
# parents[0] => .../src
# parents[1] => .../day01   <- we want this
ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"

def ensure_dirs():
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    ensure_dirs()
    print("ROOT:", ROOT)
    print("RAW:", RAW, "exists:", RAW.exists())
    print("PROCESSED:", PROCESSED, "exists:", PROCESSED.exists())
