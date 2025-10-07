from src.managers.task_manager import TaskManager

def titles_only(manager: TaskManager) -> list[str]:
    """Extract titles from display lines for clean comparisons."""
    return [line.split(" ", 1)[1] for line in manager.list_tasks()]  # e.g., "1. • A" -> "• A"

def snapshot(manager: TaskManager) -> list[str]:
    """Full list_tasks() snapshot (number + bullet + title)."""
    return list(manager.list_tasks())

m = TaskManager()
m.add_task("A"); m.add_task("B"); m.add_task("C")

# --- 1) Happy path: delete first item ---
before = snapshot(m)
ok = m.delete_task(0)
after = snapshot(m)

print("AFTER DELETE(0):")
print("\n".join(after))
assert ok is True, "Expected True on valid delete"
assert len(after) == len(before) - 1, "Count should decrease by 1"
assert after[0].startswith("1.") and "B" in after[0], "List should reindex: first line should be B"
assert after[1].startswith("2.") and "C" in after[1], "Second line should be C"

# --- 2) Guardrail: invalid high index should not mutate state ---
snap = snapshot(m)
ok2 = m.delete_task(999)
assert ok2 is False, "Invalid index should return False"
assert snapshot(m) == snap, "State must not change on invalid delete"

# --- 3) Guardrail: negative index should not mutate state ---
snap = snapshot(m)
ok3 = m.delete_task(-1)
assert ok3 is False, "Negative index should return False"
assert snapshot(m) == snap, "State must not change on invalid delete (negative)"

# --- 4) Type guard: non-int index ---
snap = snapshot(m)
ok4 = m.delete_task("0")  # type: ignore
assert ok4 is False, "Non-int index should return False"
assert snapshot(m) == snap, "State must not change on wrong type"

# --- 5) Delete all, then delete from empty list ---
m = TaskManager()
m.add_task("A")
m.add_task("B")
assert m.delete_task(0) is True
assert m.delete_task(0) is True  # deletes former 'B' now at index 0
assert m.count() == 0
snap = snapshot(m)
assert m.delete_task(0) is False, "Deleting from empty list should return False"
assert snapshot(m) == snap, "No change when deleting from empty list"

print("\n✅ Independent verification for DELETE passed.")
