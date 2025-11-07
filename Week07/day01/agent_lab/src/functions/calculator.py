from typing import Literal, Union

Operator = Literal["+", "-", "*", "/"]          # allowed operator symbols
Number = Union[int, float]                      # we accept ints or floats

def calculator(a: Number, b: Number, operator: Operator) -> float:
    """
    Simple math tool.

    Args:
        a: first number (int or float)
        b: second number (int or float)
        operator: one of "+", "-", "*", "/"

    Returns:
        The result as a float.

    Raises:
        ValueError: if operator is not supported.
    """
    # Make sure output type is consistent
    a = float(a)
    b = float(b)

    if operator == "+":
        return a + b
    elif operator == "-":
        return a - b
    elif operator == "*":
        return a * b
    elif operator == "/":
        # No crash on divide-by-zero; return +infinity like many calculators
        return a / b if b != 0.0 else float("inf")
    else:
        raise ValueError(f"Unsupported operator: {operator}")


def calculator_safe(a: Number, b: Number, operator: Operator):
    """Non-crashing wrapper useful during agent development."""
    try:
        result = calculator(a, b, operator)
        return {"ok": True, "result": result}
    except Exception as e:
        return {"ok": False, "error": str(e)}
