from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"

def ensure_dirs():
    """Create required data directories if missing."""
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    ensure_dirs()
    print("ROOT:", ROOT)
