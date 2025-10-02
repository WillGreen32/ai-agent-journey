# super_deep_dive.py

print("\n=== 1) Single inheritance: override vs extend ===")

class Task:
    def __init__(self, title):
        self.title = title
        self.log = ["Task.__init__"]

    def display(self):
        return f"Task: {self.title}"


class UrgentTask(Task):
    def __init__(self, title, priority):
        # EXTEND parent __init__ (keeps 'title' + 'log')
        super().__init__(title)
        self.priority = priority
        self.log.append("UrgentTask.__init__")

    def display(self):
        # EXTEND parent logic (could be: base + decorations)
        base = super().display()
        return f"URGENT[{self.priority}] {base}"


u = UrgentTask("fix prod bug", "HIGH")
print("display:", u.display())
print("log:", u.log)
print("MRO:", [c.__name__ for c in UrgentTask.mro()])

print("\n=== 2) Skipping super(): state loss ===")

class BadUrgentTask(Task):
    def __init__(self, title, priority):
        # NO super().__init__(title) -> parent state not set
        self.priority = priority

    def display(self):
        # Will crash: parent never created self.title
        return f"BAD[{self.priority}] {self.title}"

try:
    b = BadUrgentTask("missing init", "HIGH")
    print(b.display())
except Exception as e:
    print("Expected failure:", type(e).__name__, "-", e)
