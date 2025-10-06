from src.models.task import Task

def test_task_creation():
    t = Task("Write code")
    assert t.title == "Write code"
    assert not t.done

def test_mark_done():
    t = Task("Do work")
    t.mark_done()
    assert t.done is True
def test_imports_ok():
    import src.cli.main as app
    assert callable(app.main)
