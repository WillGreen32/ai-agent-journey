# methods_vs_functions.py
"""
Block 1 — Methods vs Standalone Functions
Goal: Compare a plain function vs a class method.
"""

# --- Standalone function (procedural style) ---
def car_info(make, model, year):
    return f"{year} {make} {model}"

print("Standalone function:", car_info("Toyota", "Corolla", 2020))


# --- Same thing with a class + method ---
class Car:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year

    def display_info(self):  # method, bound to an object
        return f"{self.year} {self.make} {self.model}"

c1 = Car("Honda", "Civic", 2019)
print("Method:", c1.display_info())
