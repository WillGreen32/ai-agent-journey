# labs/json_basics_lab.py
# (optional) shim so this file also works if you run "python labs\json_basics_lab.py"
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # adds day01 to sys.path

import json
from src.paths import PROCESSED, ensure_dirs


def describe_file(p: Path, label: str):
    text = p.read_text(encoding="utf-8")
    lines = text.splitlines()
    print(f"\n{label}: {p}")
    print("  size (bytes):", p.stat().st_size)
    print("  first line   :", lines[0] if lines else "(empty)")
    print("  last line    :", lines[-1] if lines else "(empty)")


def main():
    ensure_dirs()
    PROCESSED.mkdir(parents=True, exist_ok=True)

    # ----- A) Write pretty JSON (human-friendly) -----
    user_path = PROCESSED / "user.json"
    data = {
        "name": "Will",
        "age": 21,
        "city": "Melbourne",
        "emoji": "😀",              # non-ASCII
        "accented": "Café naïve"    # non-ASCII letters
    }

    # Pretty JSON:
    # - indent=2       : adds spaces/newlines so humans can read it
    # - ensure_ascii=False : keep real unicode (😀, é), not \u-escaped
    with open(user_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ Wrote pretty JSON")
    describe_file(user_path, "Pretty JSON (human-friendly)")

    # ----- B) Read JSON -----
    with open(user_path, encoding="utf-8") as f:
        loaded = json.load(f)
    print("\n✅ Loaded JSON")
    print("  Loaded keys:", sorted(loaded.keys()))
    print("  Loaded emoji:", loaded["emoji"])

    # ----- C) Compact JSON (machine-friendly, smaller) -----
    compact_path = PROCESSED / "user.compact.json"
    # - separators=(',', ':') removes spaces after comma/colon -> smaller file
    with open(compact_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    print("\n✅ Wrote compact JSON")
    describe_file(compact_path, "Compact JSON (space-minimized)")

    # Extra: compare sizes and show the effect of ensure_ascii=True
    ascii_path = PROCESSED / "user.ascii.json"
    with open(ascii_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=True, indent=2)  # unicode becomes \uXXXX
    print("\n✅ Wrote ensure_ascii=True JSON")
    describe_file(ascii_path, "ASCII-only JSON (unicode escaped)")

    # ----- D) Safe load with error handling -----
    broken_path = PROCESSED / "broken.json"
    # missing closing brace -> invalid JSON on purpose
    broken_path.write_text('{"name": "Oops", "age": 21  ', encoding="utf-8")

    try:
        json.loads(broken_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print("\n🛡️  Caught JSON error:")
        print(f"  file     : {broken_path}")
        print(f"  position : line {e.lineno}, col {e.colno}")
        print(f"  message  : {e.msg}")


if __name__ == "__main__":
    main()
    print("\n✅ JSON basics lab complete.")
