# OOP vs Procedural — Calculator Reflection

---

## Procedural Approach
- **How it works**: Everything is functions. Each call is isolated.
- **Strengths**:
  - Easy to understand, minimal setup.
  - Perfect for small scripts or quick throwaway tools.
- **Weaknesses**:
  - No shared state — every function call starts fresh.
  - Harder to organize as the project grows (lots of global functions).
  - Adding features means editing multiple functions (scattered logic).

---

## OOP Approach
- **How it works**: Define a class as a *blueprint*. Create objects (instances) that keep their own data.
- **Strengths**:
  - Encapsulation: logic + data live together.
  - State: objects remember information (`last_result`).
  - Extensibility: new methods can be added without breaking old code.
  - Scalability: works well across multiple files/modules.
- **Weaknesses**:
  - Slightly more verbose upfront.
  - Overkill for very small scripts.

---

## Side-by-Side Summary

| Aspect              | Procedural                        | OOP                                 |
|---------------------|-----------------------------------|-------------------------------------|
| Code organization   | Loose functions everywhere        | Methods grouped inside a class       |
| State persistence   | None (stateless)                  | Objects can hold state (`last_result`) |
| Ease of use         | Simple, fast to write             | More setup, but structured          |
| Scaling to big apps | Hard to manage, messy             | Natural fit (modules, classes, objects) |

---

## Key Takeaway
Procedural code is fine for tiny tasks.  
But OOP provides a **blueprint + memory + structure** → essential for larger, multi-file, real-world projects.
### Car Class Basics
- __init__ runs when a new object is created.
- self is the object itself.
- Each Car object has its own attributes.
- I can change attributes on one object without affecting others.
- Dynamic attributes are possible but unsafe — not all objects will have them.

### Book Class + Errors
- Python forces all __init__ args to be passed.
- Forgetting `self` breaks the method signature (Python auto-passes the instance).
- If no __init__ is defined, the class can’t take parameters.
- Good practice: define all expected attributes in __init__.
- Dynamic attributes are possible, but dangerous (inconsistent objects).

### Student Class + Good Habits
- Bad: adding attributes after creation (inconsistent objects).
- Good: define all attributes in __init__ (consistent object structure).
- Optional attributes can default to None or a placeholder.
- __dict__ shows all attributes per object.
# Defining Classes — Reflection

---

## Core Lessons
- `__init__` is the constructor: it runs every time you create an object.
- `self` refers to the current object instance (Python passes it automatically).
- All attributes should be defined inside `__init__` for consistency.
- Missing `self` → Python throws a TypeError.
- Forgetting a required parameter → Python enforces argument count.
- Adding attributes dynamically works, but leads to messy/unpredictable objects.

---

## Mistakes I Saw
- Tried to call `Book("Dune", "Frank Herbert")` → missing arg error.
- Forgot `self` in `__init__` → Python miscounted arguments.
- Added `s1.gpa` manually → inconsistent with `s2` (bad practice).
- Skipped `__init__` in `LazyBook` → class couldn’t accept parameters.

---

## Good Practices
- Always include `self` as the first parameter in instance methods.
- Keep all attributes inside `__init__` → consistent shape for every object.
- If an attribute is optional, give it a default (e.g., `gpa=None`).
- Use `__dict__` to inspect object attributes when debugging.

---

## Mini-Win
I can now:
- Define classes (`Car`, `Book`, `Student`) from scratch.
- Explain `__init__` and `self` clearly.
- Spot and avoid pitfalls (missing args, forgotten `self`, dynamic attributes).
- Write a simple class in <2 minutes without reference.

### Creating Objects — Block 1
- Each `Car(...)` or `Student(...)` call creates a new object.
- Objects have unique memory identities (`id(obj)`).
- Even if they share the same class, their data is independent.

### Creating Objects — Block 2
- Each object is independent. Updating one doesn’t affect others.
- Collections (lists) let me manage multiple objects in loops.
- __dict__ shows the actual attributes inside an object at runtime.

### Methods vs Functions — Block 1
- Standalone function requires all data each time (make, model, year).
- Method only needs `self` → the object already holds its own data.
- Functions are stateless; methods are tied to an object’s state.

### Practice Adding Methods — Block 2
- Methods operate directly on the object’s attributes (`self.make`, `self.grade`).
- Less repetition → no need to pass the same values around every time.
- Car example shows logical behavior (`is_modern`) tied to its data.
- Student example shows rules (`is_passing`) embedded into the class.
### Methods vs Functions — Block 3 Reflection

- **Instance methods (`self`)**: tied to an object, work on its attributes.
- **Class methods (`cls`)**: tied to the class itself, can see/change class-level data.
- **Static methods**: utility functions inside the class, don’t touch self/cls.

Examples:
- `summary()` → instance-level behavior.
- `count()` → tracks all instances.
- `grade_scale()` → helper, but grouped inside the class for organization.

Mini-win: I can now explain the 3 method types and show examples in code.

### Car Practice — returns vs side effects
- `display_info()` returns → reusable.
- `start_engine()` prints → immediate effect, not reusable.
- Changing one object’s attributes doesn’t affect others.
- `__dict__` helps me debug current object state.

### Student Practice — Mutability
- Objects are mutable → attributes can change after creation.
- update_grade() is safer than direct assignment because:
  - Keeps control centralized.
  - Easier to add validation later (e.g. check grade is A–F).
- Encapsulation: combine data (name, age, grade) with behaviors (get_grade, update_grade).

### Book Practice — Stateful Objects
- Objects can hold state that evolves over time.
- `Book.pages` decreases as you call `read_pages`.
- Each object is independent: b1 and b2 track their own pages.
- This is simulation modeling in miniature → objects act like real-world things.
