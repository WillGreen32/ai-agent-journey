from src.models.task import Task

def test_task_roundtrip():
    t = Task("X")
    d = t.to_dict()
    t2 = Task.from_dict(d)
    assert t2.title == "X"
    assert isinstance(t2.created_at, type(t.created_at))
    assert t2.done is False  # default persists

