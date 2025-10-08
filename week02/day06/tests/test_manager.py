import os
import json
import tempfile
import unittest
from unittest.mock import patch

from src.core.manager import TaskManager, DataLoadError


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        # isolated temp file path for each test (Windows-friendly: close it)
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.tmp.close()
        self.m = TaskManager(data_path=self.tmp.name)
        self.m.tasks = {}  # clean slate (dict keyed by id)

    def tearDown(self):
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    # ---------------- Block 1: CRUD ----------------

    def test_add_returns_id_and_in_memory(self):
        tid = self.m.add("Read book", "Clean Architecture")
        self.assertIn(tid, self.m.tasks)
        self.assertEqual(self.m.tasks[tid].title, "Read book")

    def test_edit_updates_title(self):
        tid = self.m.add("Old", "")
        self.m.edit(tid, title="New")
        self.assertEqual(self.m.tasks[tid].title, "New")

    def test_delete_removes(self):
        tid = self.m.add("X", "")
        self.m.delete(tid)
        self.assertNotIn(tid, self.m.tasks)

    def test_complete_marks_done(self):
        tid = self.m.add("Do it", "")
        self.m.complete(tid)
        self.assertTrue(self.m.tasks[tid].completed)

    def test_missing_task_raises(self):
        with self.assertRaises(KeyError):
            self.m.edit("nope", title="N/A")

    def test_complete_is_idempotent(self):
        tid = self.m.add("Once", "")
        self.m.complete(tid)
        self.m.complete(tid)  # should not crash
        self.assertTrue(self.m.tasks[tid].completed)

    # --------------- Block 2: Persistence ----------------

    def test_save_then_load_roundtrip(self):
        tid = self.m.add("Serialize", "")
        self.m.save()  # writes JSON to data_path
        fresh = TaskManager(data_path=self.tmp.name)
        fresh.load()
        self.assertIn(tid, fresh.tasks)
        self.assertEqual(fresh.tasks[tid].title, "Serialize")

    def test_load_on_missing_file_is_noop(self):
        m = TaskManager(data_path=self.tmp.name + ".missing.json")
        m.load()  # should not crash
        self.assertEqual(m.tasks, {})

    def test_load_on_empty_file_is_noop(self):
        # ensure file exists but empty
        with open(self.tmp.name, "w", encoding="utf-8") as f:
            f.write("")
        self.m.load()  # should not crash
        self.assertEqual(self.m.tasks, {})

    def test_load_corrupt_raises_dataloaderror(self):
        with open(self.tmp.name, "w", encoding="utf-8") as f:
            f.write("{not: json")
        with self.assertRaises(DataLoadError):
            self.m.load()

    def test_save_creates_directory(self):
        new_path = os.path.join(os.path.dirname(self.tmp.name), "subdir", "tasks.json")
        m = TaskManager(data_path=new_path)
        tid = m.add("Make dir", "")
        m.save()
        self.assertTrue(os.path.exists(new_path), "save() should create directories as needed")

    def test_save_is_atomic(self):
        # prime file with 1 task
        tid1 = self.m.add("Keep me", "")
        self.m.save()
        with open(self.tmp.name, "rb") as f:
            original_bytes = f.read()

        # add a second task, then simulate replace fail
        self.m.add("Might fail", "")

        with patch("os.replace", side_effect=OSError("simulated replace failure")):
            with self.assertRaises(OSError):
                self.m.save()

        # original file must remain intact; no partial write
        with open(self.tmp.name, "rb") as f:
            after_bytes = f.read()
        self.assertEqual(original_bytes, after_bytes, "Atomic save must not corrupt existing file")

    # --------------- Block 3: DI & Integrity ----------------

    def test_add_uses_injected_id_provider(self):
        def fake_id(): return "fixed-id-001"
        m = TaskManager(data_path=self.tmp.name, id_provider=fake_id)
        tid = m.add("Deterministic", "")
        self.assertEqual(tid, "fixed-id-001")
        self.assertIn("fixed-id-001", m.tasks)

    def test_add_uses_injected_now_provider(self):
        from datetime import datetime, timezone
        fixed_now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        m = TaskManager(data_path=self.tmp.name, now_provider=lambda: fixed_now)
        tid = m.add("Freeze time", "")
        self.assertEqual(m.tasks[tid].created_at, fixed_now)

    def test_json_has_consistent_ids(self):
        tid = self.m.add("Consistency", "")
        self.m.save()
        with open(self.tmp.name, "r", encoding="utf-8") as f:
            data = json.load(f)
        records = [rec for rec in data if rec["id"] == tid]
        self.assertEqual(len(records), 1, "Each saved task should have matching id")

    def test_delete_missing_task_raises_keyerror(self):
        with self.assertRaises(KeyError):
            self.m.delete("unknown-id")


if __name__ == "__main__":
    unittest.main()


