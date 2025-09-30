# calculator_oop.py
"""
OOP calculator:
- Encapsulates operations inside a class
- Keeps state (last_result)
"""

class Calculator:
    def __init__(self):
        # Every new Calculator object starts with last_result = 0
        self.last_result = 0

    def add(self, a, b):
        self.last_result = a + b
        return self.last_result

    def subtract(self, a, b):
        self.last_result = a - b
        return self.last_result

    def multiply(self, a, b):
        self.last_result = a * b
        return self.last_result

    def divide(self, a, b):
        if b == 0:
            raise ZeroDivisionError("divide by zero")
        self.last_result = a / b
        return self.last_result


if __name__ == "__main__":
    # Example usage
    calc = Calculator()
    print("OOP Calculator")
    print("5 + 2 =", calc.add(5, 2))
    print("5 - 2 =", calc.subtract(5, 2))
    print("5 * 2 =", calc.multiply(5, 2))
    print("5 / 2 =", calc.divide(5, 2))
    print("Last result stored in object:", calc.last_result)

    # Quick sanity checks
    assert calc.add(1, 1) == 2
    assert calc.subtract(10, 4) == 6
    assert calc.multiply(3, 7) == 21
    assert round(calc.divide(8, 2), 2) == 4.0
c1 = Calculator()
c2 = Calculator()

print(c1.add(10, 5))   # 15
print(c2.multiply(2, 3))  # 6

print("c1 last result:", c1.last_result)  # 15
print("c2 last result:", c2.last_result)  # 6
