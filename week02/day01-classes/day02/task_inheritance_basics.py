# task_inheritance_basics.py

# --- Parent class ---
class Task:
    category = "general"   # class attribute (shared)

    def __init__(self, title):
        self.title = title              # instance attribute

    def display(self):
        return f"Task: {self.title}"    # instance method


# Toggle to simulate the failure you saw in Step 3
FAIL_DEMO = False   # keep this False for Step 4


# --- Child class (inherits Task) ---
class UrgentTask(Task):
    def __init__(self, title, priority):
        # IMPORTANT: this must run for self.title to exist
        if not FAIL_DEMO:
            super().__init__(title)     # <-- DO NOT COMMENT THIS in Step 4
        # If you set FAIL_DEMO=True, we skip super() to show the failure
        self.priority = priority

    def display(self):
        return f"URGENT[{self.priority}]: {self.title}"


# --- Grandchild class (extends, doesn't replace) ---
class VerboseUrgentTask(UrgentTask):
    def display(self):
        # Extend the child's behavior, not replace it
        base = super().display()  # calls UrgentTask.display() (which relies on self.title)
        return base + " 🚨 handle immediately"


if __name__ == "__main__":
    # ============ DEMO RUN ============

    # 1) Base & child
    t = Task("write unit tests")
    u = UrgentTask("fix prod bug", priority="HIGH")

    print(t.display())     # Task: write unit tests
    print(u.display())     # URGENT[HIGH]: fix prod bug

    # 2) MRO + type checks
    print("MRO:", UrgentTask.mro())
    print("Is UrgentTask a Task?", issubclass(UrgentTask, Task))
    print("Is u a Task?", isinstance(u, Task))
    print("u.__dict__:", u.__dict__)

    # 3) Grandchild that EXTENDS behavior
    vu = VerboseUrgentTask("oncall incident", "CRITICAL")
    print(vu.display())    # URGENT[CRITICAL]: oncall incident 🚨 handle immediately

    # 4) Class vs instance attribute behavior
    print("Task.category:", Task.category)                 # general
    print("UrgentTask.category (inherited):", UrgentTask.category)  # general
    UrgentTask.category = "alerts"                         # shadow on child class
    print("Task.category (unchanged):", Task.category)     # general
    print("UrgentTask.category (now child-specific):", UrgentTask.category)  # alerts

    # 5) Polymorphism: treat them all as Tasks
    items = [t, u, vu]
    for item in items:
        print("Poly:", item.display())
