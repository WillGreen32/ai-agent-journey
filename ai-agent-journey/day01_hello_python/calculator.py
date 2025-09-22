# calculator.py
"""
Day 2: Simple Calculator (loop + safe input + history + extra ops)
- Operations: add/subtract/multiply/divide + modulus + power
- Shortcuts: +  -  *  /  %  **   (also 'pow', 'mod')
- Safe numeric input (floats)
- Menu loop; 'help' for help; 'history' to view last 5 ops; 'q' to quit
"""

from collections import deque

# ---------- math ops ----------
def add(x, y): return x + y
def subtract(x, y): return x - y
def multiply(x, y): return x * y
def divide(x, y):
    if y == 0:
        return "Error: Division by zero"
    return x / y
def modulus(x, y): return x % y
def power(x, y): return x ** y

# ---------- input helpers ----------
def ask_number(prompt: str) -> float:
    """Ask until the user gives a valid number (float)."""
    while True:
        raw = input(prompt).strip()
        try:
            return float(raw)
        except ValueError:
            print("Please enter a number like 12 or 3.5.")

# (Optional) whole number input
def ask_int(prompt: str) -> int:
    """Ask until user gives a valid whole number (int)."""
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Please enter a whole number (like 5).")

# ---------- UI helpers ----------
def show_menu():
    print("\n=== Simple Calculator ===")
    print("Operations: add | subtract | multiply | divide | modulus | power")
    print("Shortcuts : +   |   -     |   *      |   /    |   %     |  ** (or 'pow')")
    print("Other     : history | help | q (quit)")

def format_result(value):
    """Clean output: 4.0 -> 4; keep decimals when needed."""
    if isinstance(value, (int, float)):
        rounded = round(float(value), 6)
        return int(rounded) if rounded.is_integer() else rounded
    return value

# ---------- dispatcher ----------
OP_MAP = {
    "add": add, "+": add,
    "subtract": subtract, "-": subtract,
    "multiply": multiply, "*": multiply,
    "divide": divide, "/": divide,
    "modulus": modulus, "%": modulus, "mod": modulus,
    "power": power, "**": power, "pow": power,
}

def main():
    show_menu()
    history = deque(maxlen=5)  # keep last 5 results

    while True:
        choice = input("\nEnter operation (add/subtract/multiply/divide/modulus/power, symbols ok; help, history, q): ").strip().lower()

        # exit / help / history
        if choice in ("q", "quit", "exit"):
            print("Goodbye! 👋")
            break
        if choice == "help":
            show_menu()
            continue
        if choice == "history":
            if not history:
                print("History is empty.")
            else:
                print("Last results (newest first):")
                for idx, item in enumerate(reversed(history), start=1):
                    print(f" {idx}. {item}")
            continue

        # choose operation
        func = OP_MAP.get(choice)
        if func is None:
            print("Invalid choice. Type 'help' to see options.")
            continue

        # numbers
        num1 = ask_number("Enter first number: ")
        num2 = ask_number("Enter second number: ")

        # compute
        result = func(num1, num2)
        result_fmt = format_result(result)

        print(f"Result: {result_fmt}")

        # store only numeric results in history
        if isinstance(result, (int, float)):
            history.append(result_fmt)

if __name__ == "__main__":
    main()

# --- quick self-tests (run once, then comment) ---
# assert add(2, 3) == 5
# assert subtract(10, 7) == 3
# assert multiply(2, 8) == 16
# assert divide(9, 3) == 3
# assert divide(9, 0) == "Error: Division by zero"
# assert modulus(10, 3) == 1
# assert power(2, 3) == 8
# print("All quick tests passed!")

