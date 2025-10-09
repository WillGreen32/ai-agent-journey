import os
import json
from src.core.manager import TaskManager

def test_crud_cycle():
    m = TaskManager()
    m.add_task("A")
    assert len(m.tasks) == 1
    m.edit_task(0, "B")
    assert m.tasks[0].title == "B"
    m.delete_task(0)
    assert len(m.tasks) == 0

def test_persistence_roundtrip(tmp_path):
    fp = tmp_path / "tasks.json"
    m = TaskManager()
    m.add_task("A"); m.add_task("B")
    m.save(fp.as_posix())
    assert os.path.exists(fp)

    m2 = TaskManager()
    m2.load(fp.as_posix())
    assert [t.title for t in m2.tasks] == ["A", "B"]

import io
import sys
import os
from src.core.manager import TaskManager

def test_load_handles_empty_file(tmp_path):
    fp = tmp_path / "tasks.json"
    fp.write_text("", encoding="utf-8")  # empty file
    m = TaskManager()
    m.load(fp.as_posix())  # should not crash
    assert m.tasks == []

def test_edit_delete_raise_indexerror():
    m = TaskManager()
    m.add_task("Only")
    try:
        m.edit_task(5, "Nope")
        assert False, "Expected IndexError"
    except IndexError:
        pass
    try:
        m.delete_task(2)
        assert False, "Expected IndexError"
    except IndexError:
        pass

def test_view_tasks_prints_list(capfd):
    m = TaskManager()
    m.add_task("A"); m.add_task("B")
    m.view_tasks()
    out, _ = capfd.readouterr()
    assert "Your Tasks:" in out
    assert "1." in out and "2." in out
