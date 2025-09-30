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
