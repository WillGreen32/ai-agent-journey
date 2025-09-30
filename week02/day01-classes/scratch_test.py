class Dog:
    def __init__(self, name, breed, age):
        self.name = name
        self.breed = breed
        self.age = age

d1 = Dog("Buddy", "Golden Retriever", 3)
d2 = Dog("Milo", "Pug", 1)

print(d1.name, "-", d1.breed, "-", d1.age)
print(d2.name, "-", d2.breed, "-", d2.age)
