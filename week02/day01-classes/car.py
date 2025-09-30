class Car:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year

# test
c1 = Car("Toyota", "Corolla", 2020)
c2 = Car("Honda", "Civic", 2019)

print(c1.make, c1.model, c1.year)
print(c2.make, c2.model, c2.year)
# Different objects keep their own data
c1.make = "Nissan"     # change only c1
print("After update:")
print("Car 1:", c1.make, c1.model, c1.year)
print("Car 2:", c2.make, c2.model, c2.year)

# You can add attributes dynamically (but it’s messy)
c1.color = "Red"
print("Car 1 color:", c1.color)

# Car 2 has no color attribute
try:
    print("Car 2 color:", c2.color)
except AttributeError as e:
    print("Error:", e)
