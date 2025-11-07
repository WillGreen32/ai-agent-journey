# src/functions/calculator.py
# Simple, safe calculator (supports + - * /)

schema = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Do basic math on two numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"},
                "op": {
                    "type": "string",
                    "enum": ["+", "-", "*", "/"],
                    "description": "Math operation"
                }
            },
            "required": ["a", "b", "op"],
            "additionalProperties": False
        }
    }
}

def run(a: float, b: float, op: str):
    if op == "+": return a + b
    if op == "-": return a - b
    if op == "*": return a * b
    if op == "/":
        if b == 0:
            raise ValueError("Division by zero")
        return a / b
    raise ValueError(f"Unsupported op: {op}")
