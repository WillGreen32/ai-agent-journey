def add(x, y):
    return x + y
print(add(2, 5))
def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    return x / y
print(add(5, 3))       # 8
print(subtract(10, 4)) # 6
print(multiply(2, 7))  # 14
print(divide(20, 4))   # 5
def add(x: float, y: float) -> float:
    """Return the sum of x and y."""
    return x + y
def divide(x: float, y: float) -> float:
    """Return x divided by y, or error message if y = 0."""
    if y == 0:
        return "Error: Cannot divide by zero"
    return x / y
def average(x, y):
    """Return the average of two numbers using add + divide."""
    return divide(add(x, y), 2)

print(average(10, 20))  # 15.0
