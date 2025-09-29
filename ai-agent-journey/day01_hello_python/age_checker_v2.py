# Version 4 — Reusable helper for any integer input (with optional min/max)

from typing import Optional

def read_int(prompt: str,
             min_value: Optional[int] = None,
             max_value: Optional[int] = None) -> int:
    """Read an integer from input with optional inclusive min/max validation."""
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a whole number (e.g., 17).")
            continue

        too_small = (min_value is not None and value < min_value)
        too_large = (max_value is not None and value > max_value)
        if too_small or too_large:
            if min_value is not None and max_value is not None:
                print(f"Please enter a number between {min_value} and {max_value}.")
            elif min_value is not None:
                print(f"Please enter a number ≥ {min_value}.")
            else:
                print(f"Please enter a number ≤ {max_value}.")
            continue

        return value

# --- Use the helper for the Age Checker ---
age = read_int("Enter your age: ", min_value=0, max_value=120)
print("Adult" if age >= 18 else "Minor")
while True:
    raw = input("Enter any integer (or 'q' to quit): ").strip().lower()
    if raw == "q":
        print("Goodbye!")
        break
    try:
        n = int(raw)
    except ValueError:
        print("Whole numbers only, e.g., -3 or 42.")
        continue

    if n > 0:
        print("Positive")
    elif n == 0:
        print("Zero")
    else:
        print("Negative")



