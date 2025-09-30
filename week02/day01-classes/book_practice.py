# book_practice.py
"""
Goal: explore evolving state inside objects.
"""

class Book:
    def __init__(self, title, author, pages):
        self.title = title
        self.author = author
        self.pages = pages

    def read_pages(self, x):
        if x > self.pages:
            return f"Not enough pages left! Only {self.pages} remaining."
        self.pages -= x  # mutate internal state
        return f"{x} pages read, {self.pages} left."

b1 = Book("1984", "George Orwell", 328)

print(b1.read_pages(50))   # should reduce to 278
print(b1.read_pages(100))  # should reduce to 178
print(b1.read_pages(200))  # not enough pages
b2 = Book("Dune", "Frank Herbert", 500)
print(b2.read_pages(120))  # b2 starts fresh, independent of b1
