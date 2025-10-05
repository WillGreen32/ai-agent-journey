# src/utils.py
import re
from datetime import datetime

def slugify(text: str) -> str:
    """
    Turn any string into a URL-friendly slug.
    Examples:
      " Hello, World! " -> "hello-world"
      "A  B   C"        -> "a-b-c"
    """
    text = text.strip().lower()                  # trim + lowercase
    text = re.sub(r"[^a-z0-9]+", "-", text)      # non-alphanum -> "-"
    return re.sub(r"-{2,}", "-", text).strip("-")# collapse "--" and trim "-"

def parse_date(s: str) -> datetime:
    """
    Parse common date formats into a datetime (naive, no timezone).
    Accepted:
      - 2025-10-02           (YYYY-MM-DD)
      - 02/10/2025           (DD/MM/YYYY)
      - 2025-10-02T13:45:00  (ISO-like)
    """
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {s}")
