# tests/test_task_model.py
from datetime import datetime, timezone, timedelta
from src.models.task import Task

def test_creation_defaults_and_display():
    t = Task("  Write code  ")
    assert t.title == "Write code"
    assert t.done is False
    assert isinstance(t.created_at, datetime)
    assert t.created_at.tzinfo is not None  # timezone-aware
    s = str(t)
    assert s.startswith("• ") and "Write code" in s  # display uses bullet when not done

def test_to_dict_has_required_keys_and_iso_timestamp():
    t = Task("X")
    d = t.to_dict()
    assert set(d.keys()) == {"title", "created_at", "done"}
    # ISO-ish sanity: contains 'T' and timezone info
    assert "T" in d["created_at"]
    assert d["created_at"].endswith("+00:00") or d["created_at"].endswith("Z") or "+" in d["created_at"] or d["created_at"].endswith("-00:00")

def test_from_dict_round_trip_keeps_values():
    t = Task("Review PRs")
    t.done = True
    d = t.to_dict()
    t2 = Task.from_dict(d)
    assert t2.title == "Review PRs"
    assert t2.done is True
    # timestamps should be close (string->datetime->obj)
    # allow a small drift if clocks differ, but they shouldn't.
    assert abs((t2.created_at - t.created_at).total_seconds()) < 1.0

def test_from_dict_tolerant_missing_fields():
    # missing done -> False
    data = {"title": "Alpha", "created_at": datetime.now(timezone.utc).isoformat()}
    t = Task.from_dict(data)
    assert t.title == "Alpha"
    assert t.done is False

    # missing or invalid created_at -> now(UTC)
    t2 = Task.from_dict({"title": "Beta"})  # no created_at
    assert t2.created_at.tzinfo is not None

    t3 = Task.from_dict({"title": "Gamma", "created_at": "not-a-timestamp"})
    assert t3.created_at.tzinfo is not None

def test_rejects_empty_or_whitespace_title():
    import pytest
    with pytest.raises(ValueError):
        Task("   ")

    with pytest.raises(ValueError):
        Task.from_dict({"title": "   ", "created_at": datetime.now(timezone.utc).isoformat()})
