from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]  # project root (.../day07)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
