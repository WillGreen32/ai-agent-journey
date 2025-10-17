# tools/refactor_imports.py
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]  # .../day07

# Patterns map old imports to absolute src.* imports.
# Add/adjust as needed for your codebase.
PATTERNS = [
    (r"\bfrom\s+clean_data\s+import\b",       "from src.clean.clean_data import"),
    (r"\bfrom\s+validator\s+import\b",        "from src.validate.validator import"),
    (r"\bfrom\s+transform_data\s+import\b",   "from src.transform.transform_data import"),
    (r"\bfrom\s+reader\s+import\b",           "from src.io.reader import"),
    (r"\bimport\s+clean_data\b",              "from src.clean import clean_data"),
    (r"\bimport\s+validator\b",               "from src.validate import validator"),
    (r"\bimport\s+transform_data\b",          "from src.transform import transform_data"),
    (r"\bimport\s+reader\b",                  "from src.io import reader"),
]

def rewrite_file(py: Path) -> bool:
    text = py.read_text(encoding="utf-8")
    new = text
    for pattern, repl in PATTERNS:
        new = re.sub(pattern, repl, new)
    if new != text:
        py.write_text(new, encoding="utf-8")
        return True
    return False

def main() -> None:
    changed = 0
    for py in ROOT.rglob("*.py"):
        # Skip the refactor script itself
        if py.resolve() == Path(__file__).resolve():
            continue
        # Avoid changing files in hidden/venv dirs
        if any(part.startswith((".", "venv", ".venv", "__pycache__")) for part in py.parts):
            continue
        if "tools" in py.parts:  # don't rewrite tools by default
            continue
        if rewrite_file(py):
            print(f"Rewrote imports in {py}")
            changed += 1
    print(f"Done. Files changed: {changed}")

if __name__ == "__main__":
    main()
