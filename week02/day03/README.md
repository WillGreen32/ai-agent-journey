# Week 2 — Day 3: Modules + Project Structure

This day proves I can split code across files, expose a clean package API, run a CLI module, and verify everything with tests.

---

## ✅ What I built
- `src/` Python package:
  - `task.py` — `Task`, `UrgentTask`, `RecurringTask`, `CompletedTask`
  - `utils.py` — `slugify`, `parse_date`
  - `cli/main.py` — demo script that uses the package
- `tests/` with `pytest` for quick verification
- Clean package exports in `src/__init__.py`

---

## 📦 Project tree (key parts)
