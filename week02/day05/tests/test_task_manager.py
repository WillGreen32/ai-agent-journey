# tests/test_task_manager.py
import pytest
from src.managers.task_manager import TaskManager

def test_add_then_list_numbering_and_content():
    m = TaskManager()
    m.add_task("A")
    m.add_task("B")
    lines = m.list_tasks()
    assert lines[0].startswith("1.") and "A" in lines[0]
    assert lines[1].startswith("2.") and "B" in lines[1]
    # numbering is 1..n
    nums = [int(line.split(".")[0]) for line in lines]
    assert nums == list(range(1, m.count() + 1))

def test_edit_success_and_guardrails():
    m = TaskManager()
    m.add_task("Alpha"); m.add_task("Beta")
    # happy path
    assert m.edit_task(1, "Beta+")
    assert "Beta+" in m.list_tasks()[1]
    # bad index (too high)
    assert m.edit_task(99, "X") is False
    # bad index (negative)
    assert m.edit_task(-1, "X") is False
    # blank/whitespace title
    snap = list(m.list_tasks())
    assert m.edit_task(1, "") is False
    assert m.edit_task(1, "    ") is False
    assert list(m.list_tasks()) == snap, "No mutation on invalid title"
    # wrong type index
    assert m.edit_task("0", "Z") is False  # type: ignore

def test_delete_reindexes_and_guardrails():
    m = TaskManager()
    m.add_task("A"); m.add_task("B"); m.add_task("C")
    assert m.delete_task(0) is True
    lines = m.list_tasks()
    assert lines[0].startswith("1.") and "B" in lines[0]
    assert lines[1].startswith("2.") and "C" in lines[1]
    # bad indices do nothing
    snap = list(m.list_tasks())
    assert m.delete_task(99) is False
    assert m.delete_task(-1) is False
    assert list(m.list_tasks()) == snap
    # wrong type index
    assert m.delete_task("0") is False  # type: ignore

def test_add_trims_and_rejects_empty_via_model():
    m = TaskManager()
    # add_task will call Task(title=...), which raises on empty/space-only
    with pytest.raises(ValueError):
        m.add_task("   ")
    # normal add still works
    t = m.add_task("  X  ")
    assert t.title == "X"

