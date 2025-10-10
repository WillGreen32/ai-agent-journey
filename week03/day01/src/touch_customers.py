from pathlib import Path
from src.paths import RAW, ensure_dirs

def main():
    ensure_dirs()
    target = RAW / "customers.csv"

    if not target.exists():
        target.write_text("Name,Email\n", encoding="utf-8")
        print(f"📝 Created file: {target}")
    else:
        print(f"✅ Already exists: {target}")

if __name__ == "__main__":
    main()
