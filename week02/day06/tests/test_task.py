import unittest
from datetime import datetime, timedelta, timezone
from src.models.task import Task


class TestTaskModel(unittest.TestCase):
    def setUp(self):
        self.t = Task(title="Write tests", description="Day 6", completed=False)

    # --- Init defaults ---
    def test_init_defaults(self):
        self.assertEqual(self.t.title, "Write tests")
        self.assertFalse(self.t.completed)
        self.assertIsInstance(self.t.created_at, datetime)
        # created_at should be "recent" (± 5 sec window)
        now_utc = datetime.now(timezone.utc)
        self.assertLess(now_utc - self.t.created_at, timedelta(seconds=5))

    # --- Complete ---
    def test_complete_marks_done(self):
        self.t.complete()
        self.assertTrue(self.t.completed, "complete() should set completed=True")

    def test_complete_is_idempotent(self):
        self.t.complete()
        self.t.complete()  # should not raise or change meaning
        self.assertTrue(self.t.completed)

    # --- Edit (happy path) ---
    def test_edit_updates_fields(self):
        self.t.edit(title="Write better tests", description="Add edges")
        self.assertEqual(self.t.title, "Write better tests")
        self.assertIn("edges", self.t.description)

    # --- Validation: title rules ---
    def test_invalid_title_raises(self):
        with self.assertRaises(ValueError):
            self.t.edit(title="")
        with self.assertRaises(ValueError):
            self.t.edit(title="   ")

    def test_title_whitespace_is_stripped(self):
        self.t.edit(title="   New Title  ")
        self.assertEqual(self.t.title, "New Title")

    def test_title_none_means_no_change(self):
        old = self.t.title
        self.t.edit(title=None)
        self.assertEqual(self.t.title, old)

    def test_title_max_length_enforced(self):
        too_long = "x" * 121
        with self.assertRaises(ValueError):
            self.t.edit(title=too_long)

    # --- Description behavior ---
    def test_description_none_means_no_change(self):
        old = self.t.description
        self.t.edit(description=None)
        self.assertEqual(self.t.description, old)

    def test_title_unchanged_when_description_only(self):
        old_title = self.t.title
        self.t.edit(description="Changed only desc")
        self.assertEqual(self.t.title, old_title)

    # --- Subtests for invalid titles ---
    def test_bulk_invalid_titles_with_subtests(self):
        for bad in ["", " ", "\n", "\t", "   "]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.t.edit(title=bad)

    # --- Round-trip (to_dict / from_dict) ---
def test_serialize_roundtrip(self):
    data = self.t.to_dict()
    t2 = Task.from_dict(data)
    self.assertEqual(t2.title, self.t.title)
    self.assertEqual(t2.description, self.t.description)
    self.assertEqual(t2.completed, self.t.completed)
    self.assertIsInstance(t2.created_at, datetime)

def test_id_is_preserved_across_roundtrip(self):
    original_id = self.t.id
    t2 = Task.from_dict(self.t.to_dict())
    self.assertEqual(t2.id, original_id)

def test_created_at_is_iso8601_string_in_dict(self):
    d = self.t.to_dict()
    self.assertIsInstance(d["created_at"], str)

def test_from_dict_ignores_unknown_keys(self):
    d = self.t.to_dict()
    d["unknown_field"] = "ignore_me"
    t2 = Task.from_dict(d)
    self.assertFalse(hasattr(t2, "unknown_field"))

def test_to_dict_has_minimum_schema(self):
    d = self.t.to_dict()
    for key in ("id", "title", "description", "completed", "created_at"):
        with self.subTest(key=key):
            self.assertIn(key, d)

# --- Integrity guard: created_at is immutable during edit ---
def test_created_at_immutable(self):
    original = self.t.created_at
    self.t.edit(description="change only")
    self.assertEqual(self.t.created_at, original)



if __name__ == "__main__":
    unittest.main()
