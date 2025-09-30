# car_practice.py
"""
Goal: feel the difference between 'returns a value' vs 'prints a side effect'.
"""

class Car:
    def __init__(self, make, model, year):
        # attributes (data) unique to each car
        self.make = make
        self.model = model
        self.year = year

    def display_info(self):
        # returns a string (pure; no side effect)
        return f"{self.year} {self.make} {self.model}"

    def start_engine(self):
        # prints (side effect)
        print(f"{self.model} engine started!")


# --- Usage / demo ---
c1 = Car("Toyota", "Corolla", 2020)
c2 = Car("Tesla", "Model 3", 2022)
c3 = Car("Honda", "Civic", 2019)

print(c1.display_info())
print(c2.display_info())
print(c3.display_info())

c1.start_engine()
c2.start_engine()
c3.start_engine()

# 1) Return vs print: capture returned value for later use
line = c2.display_info()          # <- returned string
banner = f"-> Featured: {line} <-"
print(banner)

# 2) Objects are independent
c1.make = "Nissan"                # change only c1
print("After change:", c1.display_info(), "| unaffected:", c2.display_info())

# 3) Inspect current state
print("c1 attributes:", c1.__dict__)
print("c2 attributes:", c2.__dict__)

