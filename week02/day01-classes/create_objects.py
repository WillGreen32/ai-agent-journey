from car import Car
from student import Student

# --- Car objects ---
c1 = Car("Toyota", "Corolla", 2020)
c2 = Car("Honda", "Civic", 2019)

print("Car 1:", c1.make, c1.model, c1.year)
print("Car 2:", c2.make, c2.model, c2.year)

# --- Student objects ---
s1 = Student("Alice", 20, "A")
s2 = Student("Bob", 21, "B")

print("Student 1:", s1.name, s1.age, s1.grade)
print("Student 2:", s2.name, s2.age, s2.grade)

# --- Identity checks ---
print("\nIdentity (id) — unique per object:")
print("c1 id:", id(c1))
print("c2 id:", id(c2))
print("s1 id:", id(s1))
print("s2 id:", id(s2))

# --- Independence of objects ---
c1.make = "Nissan"   # change only Car 1
print("\nAfter updates:")
print("Updated Car 1:", c1.make, c1.model, c1.year)
print("Car 2 unaffected:", c2.make, c2.model, c2.year)

s1.grade = "B"   # update Alice's grade
print("Updated Student 1:", s1.name, s1.grade)
print("Student 2 unaffected:", s2.name, s2.grade)

# --- Prove independence with a list of cars ---
cars = [
    Car("Ford", "Focus", 2018),
    Car("Mazda", "3", 2021),
    Car("Tesla", "Model 3", 2022),
]

print("\nLooping through a collection of Car objects:")
for car in cars:
    print("Looped Car:", car.make, car.model, car.year)

# --- Inspect attributes dynamically ---
print("\nInspecting object attributes (__dict__):")
print("c1 attributes:", c1.__dict__)
print("s1 attributes:", s1.__dict__)
