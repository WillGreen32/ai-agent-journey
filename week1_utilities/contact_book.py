"""
Contact Book (CLI)
Add, search, delete, and list contacts (name → phone). Includes input validation and clear error messages.
"""

# contacts_lookup.py
"""
Simple fruit price lookup with add/delete.
- Safe lookups (KeyError handled)
- Input validation for price (ValueError handled)
- Friendly loop with commands
"""

prices = {"apple": 2.5, "banana": 1.8}

while True:
    cmd = input("\nType a fruit name to look up, 'add', 'del', 'show', or 'q' to quit: ").strip().lower()

    if cmd == "q":
        print("Goodbye!")
        break

    if cmd == "show":
        if not prices:
            print("(No items yet)")
        else:
            for k, v in prices.items():
                print(f"- {k}: {v}")
        continue

    if cmd == "add":
        name = input("New fruit name: ").strip().lower()
        price = input("Price: ").strip()
        try:
            prices[name] = float(price)  # may raise ValueError
            print(f"Added {name} -> {prices[name]}")
        except ValueError:
            print("Price must be a number (e.g., 2.5).")
        continue

    if cmd == "del":
        name = input("Fruit to delete: ").strip().lower()
        # pop with default avoids KeyError
        removed = prices.pop(name, None)
        if removed is None:
            print("That fruit wasn't found.")
        else:
            print(f"Deleted {name} (was {removed})")
        continue

    # Normal lookup path (demonstrate try/except)
    try:
        print(f"Price: {prices[cmd]}")  # raises KeyError if missing
    except KeyError:
        print("Key not found.")
def parse_price(raw: str):
    """Return float price from messy input like '$1,234.50', or raise ValueError."""
    clean = raw.strip().replace("$", "").replace(",", "")
    return float(clean)
