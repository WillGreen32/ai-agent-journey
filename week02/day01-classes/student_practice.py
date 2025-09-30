# student_practice.py
"""
Goal: practice mutability + controlled updates.
"""

class Student:
    def __init__(self, name, age, grade):
        self.name = name
        self.age = age
        self.grade = grade

    def get_grade(self):
        """Getter → safe way to read grade."""
        return self.grade

    def update_grade(self, new_grade):
        """Setter → safe way to update grade."""
        self.grade = new_grade

s1 = Student("Alice", 20, "A")
s2 = Student("Bob", 21, "B")
s3 = Student("Charlie", 19, "C")

print("Before update:", s1.get_grade(), s2.get_grade(), s3.get_grade())

s2.update_grade("A")  # Bob improved
print("After update:", s1.get_grade(), s2.get_grade(), s3.get_grade())

# Direct attribute change (works, but not best practice)
s3.grade = "F"
print("Directly changed Charlie's grade:", s3.get_grade())

# Inspect object state
print("s1 attributes:", s1.__dict__)
print("s2 attributes:", s2.__dict__)
print("s3 attributes:", s3.__dict__)
