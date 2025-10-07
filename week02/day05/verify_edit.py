from src.managers.task_manager import TaskManager

def lines(m):  # snapshot helper
    return list(m.list_tasks())

m = TaskManager()
m.add_task("A")
m.add_task("B")

# 1) Happy path: edit index 1 (second task)
before = lines(m)
ok = m.edit_task(1, "B2")
after = lines(m)

print("\n".join(after))
assert ok is True, "Expected True on valid edit"
assert any("B2" in s for s in after), "Title should be updated to B2"
assert len(after) == len(before), "Edit must not change task count"

# 2) Whitespace normalization
ok2 = m.edit_task(1, "   B3   ")
after2 = lines(m)
assert ok2 is True, "Edit with padded spaces should succeed"
assert any(s.endswith("B3") for s in after2), "Title should be trimmed to 'B3'"

# 3) Guardrails: out-of-range
snap = lines(m)
assert m.edit_task(99, "X") is False, "Should fail on invalid index"
assert lines(m) == snap, "State must not change on invalid index"

# 4) Guardrails: blank/whitespace title
snap = lines(m)
assert m.edit_task(1, "") is False
assert m.edit_task(1, "   ") is False
assert lines(m) == snap, "State must not change on blank title"

# 5) Guardrails: wrong type for index
snap = lines(m)
assert m.edit_task("0", "Z") is False  # type: ignore
assert lines(m) == snap, "State must not change on wrong index type"

print("✅ Independent verification passed")
