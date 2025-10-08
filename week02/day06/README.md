## Day 6 — Unit Testing

We added a full `unittest` suite covering:

- **Task model**: init defaults, `edit()` validation (empty/whitespace/max length), `complete()`, `to_dict()` / `from_dict()` round-trip.
- **TaskManager**: CRUD (`add`/`edit`/`delete`/`complete`), deterministic ID/time via dependency injection, JSON **save/load** with **atomic writes**, corrupt/missing/empty file handling, and ID consistency (`task.id == JSON id == dict key`).

### Run Tests
```bash
python -m unittest discover -s tests -p "test_*.py" -v
# or (if you use pytest)
pytest -q
