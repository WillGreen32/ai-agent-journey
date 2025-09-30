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
