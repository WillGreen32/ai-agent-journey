# car_student.py
"""
Day 1 summary runner:
- Car, Student, Book classes
"""

from car_practice import Car
from student_practice import Student
from book_practice import Book

# --- Car ---
c = Car("Toyota", "Corolla", 2020)
print(c.display_info())
c.start_engine()

# --- Student ---
s = Student("Alice", 20, "A")
print(s.name, "grade:", s.get_grade())
s.update_grade("B")
print(s.name, "updated grade:", s.get_grade())

# --- Book ---
b = Book("1984", "George Orwell", 328)
print(b.read_pages(50))
print(b.read_pages(300))
