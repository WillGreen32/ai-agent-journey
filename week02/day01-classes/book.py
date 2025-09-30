# book.py
"""
Day 1 — Book class + error experiments
Goal: See what happens when you forget __init__ args or self.
"""

# --- Correct class ---
class Book:
    def __init__(self, title, author, year):
        self.title = title
        self.author = author
        self.year = year

# Correct usage
b1 = Book("1984", "George Orwell", 1949)
print("Correct Book:", b1.title, "-", b1.author, "-", b1.year)

# --- Error #1: Missing parameter ---
try:
    b2 = Book("Dune", "Frank Herbert")  # forgot year
except TypeError as e:
    print("Error (missing arg):", e)

# --- Error #2: Forgot self ---
try:
    class BrokenBook:
        def __init__(title, author):  # ❌ missing self
            title = title
            author = author

    b3 = BrokenBook("Test", "Someone")
except Exception as e:
    print("Error (forgot self):", e)

# --- Error #3: Forget __init__ entirely ---
class LazyBook:
    pass

try:
    lb = LazyBook("Nope", "Nobody", 2025)  # __init__ missing
except TypeError as e:
    print("Error (no __init__ defined):", e)
# Inspect attributes of the correct book
print("Attributes of b1:", b1.__dict__)

# Add a new attribute dynamically
b1.genre = "Dystopian"
print("After adding genre dynamically:", b1.__dict__)
