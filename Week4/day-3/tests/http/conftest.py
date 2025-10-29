
import sys
from pathlib import Path

# Ensure day-3 root is on sys.path so 'src' resolves when running tests from anywhere
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
