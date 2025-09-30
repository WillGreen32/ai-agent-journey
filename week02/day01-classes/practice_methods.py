# practice_methods.py

# --- Car class with methods ---
class Car:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year

    def display_info(self):
        """Return formatted car details."""
        return f"{self.year} {self.make} {self.model}"

    def is_modern(self):
        """Check if car is 2020 or newer."""
        return self.year >= 2020


# --- Try it out ---
c1 = Car("Toyota", "Corolla", 2010)
c2 = Car("Tesla", "Model 3", 2022)

print(c1.display_info(), "| Modern?", c1.is_modern())
print(c2.display_info(), "| Modern?", c2.is_modern())

# --- Student class with methods ---
class Student:
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade

    def is_passing(self):
        """Return True if grade is passing (A–C)."""
        return self.grade in ("A", "B", "C")


# --- Try it out ---
s1 = Student("Alice", "A")
s2 = Student("Bob", "F")

print(s1.name, "passing?", s1.is_passing())
print(s2.name, "passing?", s2.is_passing())
# --- Instance method example ---
class Student:
    all_students = []  # class-level list shared by all students

    def __init__(self, name, grade):
        self.name = name
        self.grade = grade
        Student.all_students.append(self)

    def summary(self):
        return f"Student {self.name} has grade {self.grade}"

    @classmethod
    def count(cls):
        return len(cls.all_students)

    @staticmethod
    def grade_scale(score):
        """Static method: utility function, doesn’t use self or cls"""
        if score >= 85: return "A"
        elif score >= 70: return "B"
        elif score >= 50: return "C"
        else: return "F"


# Demo
print("Total students created:", Student.count())
s1 = Student("Alice", "A")
print(s1.summary())
print("Score 72 => Grade:", Student.grade_scale(72))
print("Score 40 => Grade:", Student.grade_scale(40))
