# calculator_procedural.py
"""
Procedural calculator (no classes, no stored state):
- Pure functions for each operation
- A small dispatcher to map an operator string to a function
- A tiny CLI so you can run: python calculator_procedural.py 5 add 2
"""

from __future__ import annotations

# --- Pure operations (procedural style) ---
def add(a: float, b: float) -> float:
    return a + b

def subtract(a: float, b: float) -> float:
    return a - b

def multiply(a: float, b: float) -> float:
    return a * b

def divide(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("divide by zero")
    return a / b

# --- Dispatcher: maps a string operator to a function ---
OPERATIONS = {
    "add": add, "+": add,
    "subtract": subtract, "sub": subtract, "-": subtract,
    "multiply": multiply, "mul": multiply, "*": multiply,
    "divide": divide, "div": divide, "/": divide,
}

def compute(a: float, op: str, b: float) -> float:
    """Look up the op in OPERATIONS and apply it."""
    try:
        fn = OPERATIONS[op]
    except KeyError:
        allowed = ", ".join(sorted(set(OPERATIONS.keys())))
        raise ValueError(f"Unknown op '{op}'. Allowed: {allowed}")
    return fn(a, b)

def main() -> None:
    import argparse
    p = argparse.ArgumentParser(description="Procedural calculator")
    p.add_argument("a", type=float, help="Left operand")
    p.add_argument("op", type=str,   help="Operator (add,+,sub,-,mul,*,div,/)")
    p.add_argument("b", type=float, help="Right operand")
    p.add_argument("-q", "--quiet", action="store_true", help="Print only the result")
    args = p.parse_args()

    try:
        result = compute(args.a, args.op, args.b)
    except Exception as e:
        print(f"Error: {e}")
        raise SystemExit(1)

    if args.quiet:
        print(result)
    else:
        print(f"{args.a} {args.op} {args.b} = {result}")

if __name__ == "__main__":
    # quick smoke tests (procedural checking)
    assert add(5, 2) == 7
    assert subtract(5, 2) == 3
    assert multiply(5, 2) == 10
    assert divide(5, 2) == 2.5
    main()
