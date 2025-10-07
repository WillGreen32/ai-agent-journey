from src.managers.task_manager import TaskManager

m = TaskManager()
ok = m.load_from_json("data/tasks_test.json")
print("Load returned:", ok)
for line in m.list_tasks():
    print(line)
print("Count:", m.count())
print("✅ Load verification script finished.")
