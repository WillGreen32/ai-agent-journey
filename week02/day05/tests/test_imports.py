def test_imports_and_entrypoint():
    import src.cli.main as app
    from src.managers.task_manager import TaskManager
    assert callable(app.main)
    m = TaskManager()
    assert m.count() == 0
