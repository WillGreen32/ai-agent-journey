from src.managers.task_manager import TaskManager

DATA = "data/_e2e.json"

# 1) Save path
m = TaskManager()
m.add_task("Alpha")
m.add_task("Beta")
assert m.save_to_json(DATA), "save_to_json() should return True"

# 2) Load path (fresh instance)
n = TaskManager()
assert n.load_from_json(DATA), "load_from_json() should return True"
lines = n.list_tasks()
print("\n".join(lines))
assert "Alpha" in lines[0] and "Beta" in lines[1]
print("✅ E2E OK")
