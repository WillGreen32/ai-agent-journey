d1 = Demo()
d2 = Demo()

# instance method
print(d1.instance_method())  
print(d2.instance_method())

# class method
print(Demo.class_method())
Demo.kind = "changed"
print(Demo.class_method())

# static method
print(Demo.static_method(10, 20))
### Employee → Manager (super() demo)
- `Employee`: base attributes (`name`, `eid`, `role`, `start_date`), `describe()`, `tenure_years()`
- `Manager(Employee)`: team management (`add_report/remove_report/headcount`), overrides `describe()` using `super()`
- Negative test shows why skipping `super().__init__` breaks required state

### super() break/fix drills
- **Drill A:** `ManagerNoSuper` crashes because base attributes (`name`, `eid`) are never created; fixed by calling `super().__init__`.
- **Drill B:** Multiple inheritance: direct `Parent.__init__` call skips other bases in the MRO. Fixed by **cooperative super** (`super().__init__(*args, **kwargs)`) in every class.
# Day 2 — Methods + Inheritance

## Review Notes

- **Instance vs Class vs Static**
  - Instance = tied to `self`, unique per object
  - Class = tied to `cls`, shared across class
  - Static = independent utility, organized inside the class

- **What super() does**
  - Calls the *next class in the MRO*
  - Ensures parents/mixins set state or run behavior
  - Prevents skipping or double-calling in multiple inheritance

- **Overriding vs Rewriting**
  - Rewriting discards parent logic (danger: missing state)
  - Overriding with `super()` extends safely
  - Example: `GuardDog.speak()` keeps `Woof!` and adds `Grrr...`

## Mini-Win
I can now:
- Differentiate instance/class/static methods
- Use `super()` correctly in both single and multiple inheritance
- Decide when to override instead of rewrite

### UrgentTask
- Inherits from Task, forces status="urgent".
- Adds `priority_level` to rank urgency.
- Provides `escalate()` method to bump urgency.
- Overrides `__str__` for `[URGENT-x]` formatting.
- Uses `super().__init__` to preserve all base validation/state logic.

**RecurringTask**
- Overrides `complete()` to *extend* base behavior:
  - Calls `super().complete()` to record the occurrence
  - Immediately `reset()` to `pending` for the next cycle
- Validates `frequency` and tracks `occurrence_count` / `last_completed_at`
- Works cleanly with the base transition table (`COMPLETED → PENDING` allowed)

**CompletedTask (locked)**
- Forced `status=completed` via `super().__init__`.
- Blocks `start()`, `reset()`, `mark_urgent()` (immutable).
- `complete()` is a no-op (or raise if stricter policy preferred).
- Adds `date_completed` for audit/UX and custom `__str__`.

### Polymorphism demo + assertions
- Mixed list of `Task` + subclasses shows different `__str__` outputs via one interface.
- Behavior checks:
  - `RecurringTask.complete()` auto-resets to `pending`.
  - `CompletedTask.start()` raises (immutable).
  - `WorkTask.assign()/unassign()` updates owner rendering.
  - `UrgentTask.escalate()` bumps priority; `complete()` still uses base transition.
- Assertions verify enum-aware statuses and owner string.
