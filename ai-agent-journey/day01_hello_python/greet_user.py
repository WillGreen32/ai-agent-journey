"""
Day 1: Greet the user and compute a fun fact.
- Asks for name and age
- Validates age is a positive integer
- Prints a friendly, formatted message
"""

from datetime import date

THIS_YEAR = date.today().year


def ask_name() -> str:
    """Return a trimmed name, or 'Friend' if the user hits Enter."""
    name = input("What's your name? ").strip()
    return name or "Friend"


def ask_age() -> int:
    """Keep asking until the user enters an integer in [1..120]."""
    while True:
        raw = input("How old are you? ").strip()
        try:
            age = int(raw)
            if 1 <= age <= 120:
                return age
            print("Please enter a realistic positive age (1–120).")
        except ValueError:
            print("Please enter a whole number (e.g., 25).")


def main() -> None:
    name = ask_name()
    age = ask_age()
    birth_year = THIS_YEAR - age

    print("-" * 40)
    print(f"Hello, {name} 👋")
    print(f"You are {age} years old, so you were likely born in {birth_year}.")
    print(f"Fun: In 10 years you’ll be {age + 10}. Keep building!")
    print("-" * 40)


if __name__ == "__main__":
    main()


