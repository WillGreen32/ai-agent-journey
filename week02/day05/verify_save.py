from src.managers.task_manager import TaskManager
from pathlib import Path
import json, re

OUT = Path("data/tasks_test.json")

m = TaskManager()
m.add_task("Write report 📝")
m.add_task("Review PRs")

assert m.save_to_json(OUT), "save_to_json should return True"

# 1) File exists and is UTF-8
assert OUT.exists(), "JSON file not created"

raw = OUT.read_text(encoding="utf-8")
print("---- Raw file ----")
print(raw)

# 2) JSON parses to list of dict
data = json.loads(raw)
assert isinstance(data, list), "Top-level should be a list"
assert all(isinstance(d, dict) for d in data), "Items should be dicts"

# 3) Required keys present
for d in data:
    for k in ("title", "created_at", "done"):
        assert k in d, f"Missing key {k}"

# 4) ISO8601-ish timestamp sanity (contains 'T' and timezone)
iso_like = re.compile(r".+T.+")
assert all(iso_like.match(d["created_at"]) for d in data), "created_at should look ISO8601-like"

print("✅ Save-to-JSON verification passed.")
