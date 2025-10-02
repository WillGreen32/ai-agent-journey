# animal_oop.py

class Animal:
    """Base class. Subclasses MUST override speak()."""
    population = 0  # class attribute shared by all animals

    def __init__(self, name: str):
        if not self.validate_name(name):
            raise ValueError("name must be a non-empty string")
        self.name = name
        Animal.population += 1

    def speak(self) -> str:
        """All children must implement this; base raises to enforce."""
        raise NotImplementedError("Subclasses must implement speak()")

    @classmethod
    def get_population(cls) -> int:
        return cls.population

    @staticmethod
    def validate_name(name) -> bool:
        return isinstance(name, str) and name.strip() != ""

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"


class Dog(Animal):
    def __init__(self, name: str, breed: str = "Mixed"):
        super().__init__(name)       # keep base setup (name, population)
        self.breed = breed

    def speak(self) -> str:
        return "Woof!"


class Cat(Animal):
    def __init__(self, name: str, lives_left: int = 9):
        super().__init__(name)
        self.lives_left = lives_left

    def speak(self) -> str:
        return "Meow."


class Bird(Animal):
    def __init__(self, name: str, can_fly: bool = True):
        super().__init__(name)
        self.can_fly = can_fly

    def speak(self) -> str:
        return "Chirp!"

class GuardDog(Dog):
    def __init__(self, name: str, breed: str = "Mixed", duty_area: str = "Front Gate"):
        super().__init__(name, breed)   # ensure name populated + population tracked
        self.duty_area = duty_area

    def speak(self) -> str:
        # EXTEND Dog.speak() rather than replace it entirely
        base = super().speak()          # "Woof!"
        return base + " Grrr..."        # "Woof! Grrr..."

# --- NEGATIVE TEST CLASS (insert below GuardDog, above __main__) ---
class SilentAnimal(Animal):
    """Intentionally DOES NOT override speak() to demonstrate enforcement."""
    pass
# --- END NEGATIVE TEST CLASS ---


if __name__ == "__main__":
    # Create one of each
    d = Dog("Rex", breed="Border Collie")
    c = Cat("Luna")
    b = Bird("Tweety", can_fly=True)
    g = GuardDog("Atlas", breed="German Shepherd", duty_area="Warehouse")
    print(g, ":", g.speak())            # GuardDog(Atlas) : Woof! Grrr...
    
    print("\n-- Negative test: subclass forgot to override speak() --")
try:
    s = SilentAnimal("Ghost")
    print("Is instance of Animal?", isinstance(s, Animal))  # True
    print("SilentAnimal MRO:", SilentAnimal.mro())
    # This line should raise NotImplementedError (from Animal.speak)
    print("Attempting to speak:", s.speak())
except NotImplementedError as e:
    print("Enforcement works →", e.__class__.__name__, "-", e)


    # Individual behavior
    print(d, ":", d.speak())   # Dog(Rex) : Woof!
    print(c, ":", c.speak())   # Cat(Luna) : Meow.
    print(b, ":", b.speak())   # Bird(Tweety) : Chirp!

    # Polymorphism — same interface, different implementations
    zoo = [d, c, b]
    for a in zoo:
        print("Polymorphic speak →", a.speak())

    # Class method vs instance
    print("Animal population:", Animal.get_population())

    # MRO checks (how Python resolves attributes/methods)
    print("Dog MRO:", Dog.mro())
print("\n-- Polymorphism: same interface, different outputs --")
zoo = [
    Dog("Rex", breed="Border Collie"),
    Cat("Luna"),
    Bird("Tweety", can_fly=True),
    GuardDog("Atlas", breed="German Shepherd", duty_area="Warehouse"),
]
for a in zoo:
    print(f"{a.__class__.__name__}({a.name}) -> {a.speak()}")
print("\n-- Mini report (name, type, output) --")
rows = [(a.name, a.__class__.__name__, a.speak()) for a in zoo]
for name, typ, out in rows:
    print(f"{name:<10} | {typ:<10} | {out}")
print("\n-- Quick assertions --")
assert any(isinstance(a, Dog) and a.speak() == "Woof!" for a in zoo)
assert any(isinstance(a, Cat) and a.speak() == "Meow." for a in zoo)
assert any(isinstance(a, Bird) and a.speak() == "Chirp!" for a in zoo)
assert any(isinstance(a, GuardDog) and a.speak().startswith("Woof!") for a in zoo)
print("Assertions passed: each subclass returns its own output.")

    
    

    

