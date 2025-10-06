# Day 4 — Task Manager v1 (Core CLI)

## Overview
Built a simple but fully functional Task Manager CLI as the first CRUD app.
Focused on encapsulation, reusable functions, and clean input loops.

### 🧠 Learned
- CLI input loops and menu structures
- Encapsulation with `Task` class
- CRUD pattern (Create + Read so far)
- How to structure `src/` with packages
- Testing model behaviour with `pytest`

### 🏗️ Built
- **Task model** (`src/models/task.py`)
  - Stores title, created timestamp, done flag
  - `mark_done()` + `to_display()` for formatted output
- **CLI app** (`src/cli/main.py`)
  - Options: Add, View, Quit
  - Defensive input handling and aligned display

### ✅ Tests
- `tests/test_task_model.py` → validates model creation + mark_done
- `tests/test_cli_smoke.py` → ensures CLI imports correctly

### 🚀 Run & Test
```bash
# from week02/day04
python -m src.cli.main     # run the interactive CLI
pytest -q                  # run test suite
