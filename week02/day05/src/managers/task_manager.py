import json
from pathlib import Path
from typing import List
from src.models.task import Task

def _clean_title(v: str) -> str: return v.strip()

class TaskManager:
    def __init__(self) -> None:
        self.tasks: List[Task] = []

    # --- CRUD (from Sprint 2) ---
    def add_task(self, title: str) -> Task:
        t = Task(title=_clean_title(title))
        self.tasks.append(t)
        return t

    def list_tasks(self) -> list[str]:
        return [f"{i}. {t}" for i, t in enumerate(self.tasks, start=1)]

    def count(self) -> int:
        return len(self.tasks)

    def _valid_index(self, i: int) -> bool:
        return isinstance(i, int) and 0 <= i < len(self.tasks)

    def edit_task(self, i: int, new_title: str) -> bool:
        if not self._valid_index(i): return False
        new = _clean_title(new_title)
        if not isinstance(new_title, str) or not new: return False
        self.tasks[i].title = new
        return True

    def delete_task(self, i: int) -> bool:
        if not self._valid_index(i): return False
        del self.tasks[i]
        return True

    # --- Sprint 3: Persistence ---
    def save_to_json(self, path: str | Path = "data/tasks.json") -> bool:
        """
        Durable save:
        - Creates parent dirs
        - Writes to temp file, then atomic replace (prevents half-written JSON)
        - Pretty, UTF-8, keeps emojis (ensure_ascii=False)
        Returns True on success, False on failure.
        """
        try:
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)

            payload = [t.to_dict() for t in self.tasks]

            tmp = path.with_suffix(path.suffix + ".tmp")
            with tmp.open("w", encoding="utf-8", newline="\n") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
                f.write("\n")  # nice newline for diffs

            tmp.replace(path)  # atomic on most OSes (including NTFS)
            return True
        except Exception as e:
            print(f"⚠️  Save failed: {e}")
            return False

    def load_from_json(self, path: str | Path = "data/tasks.json") -> bool:
        """
        Tolerant load:
        - If file missing or top-level invalid → return False (no crash)
        - If some rows are bad → skip them, load the rest, return True
        - Overwrites current in-memory tasks
        """
        path = Path(path)
        if not path.exists():
            print("ℹ️  No saved tasks found.")
            return False

        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except Exception as e:
            print(f"⚠️  Load failed: {e}")
            return False

        if not isinstance(data, list):
            print("⚠️  Load failed: top-level JSON must be a list")
            return False

        loaded: List[Task] = []
        skipped = 0
        for row in data:
            try:
                loaded.append(Task.from_dict(row))
            except Exception:
                skipped += 1  # bad row → skip

        self.tasks = loaded
        if skipped:
            print(f"ℹ️  Loaded {len(loaded)} tasks, skipped {skipped} invalid row(s).")
        return True



