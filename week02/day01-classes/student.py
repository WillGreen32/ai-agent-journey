# student.py
"""
Day 1 — Student class + good habits
Goal: Practice defining attributes properly and see why dynamic attributes are bad.
"""

class Student:
    def __init__(self, name, age, grade, gpa=None):
        self.name = name
        self.age = age
        self.grade = grade
        self.gpa = gpa   # default None


# --- Create two students ---
s1 = Student("Alice", 20, "A")
s2 = Student("Bob", 21, "B")

print("Student 1:", s1.name, s1.age, s1.grade)
print("Student 2:", s2.name, s2.age, s2.grade)

# --- BAD PRACTICE: add attribute after creation ---
s1.gpa = 3.8   # only s1 has GPA
print("s1 GPA:", s1.gpa)

# s2 has no GPA → crash
try:
    print("s2 GPA:", s2.gpa)
except AttributeError as e:
    print("Error:", e)
# Inspect what attributes each student has
print("s1 attributes:", s1.__dict__)
print("s2 attributes:", s2.__dict__)
