def test_public_api():
    from src import Task, slugify
    assert callable(slugify)
    assert Task.__name__ == "Task"
