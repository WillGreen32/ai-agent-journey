from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from typing import Callable, Dict, List, Tuple

from src.models.task import Task


class DataLoadError(Exception):
    """Raised when persisted data exists but contains invalid/corrupt JSON."""


class TaskManager:
        # DI for path, id generation, and current time
    def __init__(
        self,
        data_path: str = "data/tasks.json",
        id_provider: Callable[[], uuid.UUID] = uuid.uuid4,
        now_provider: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ) -> None:
        self.data_path = data_path
        self.id_provider = id_provider
        self.now_provider = now_provider
        self.tasks: Dict[str, Task] = {}

    # ---------- Pure logic (no I/O) ----------
    def add(self, title: str, description: str = "") -> str:
        tid = str(self.id_provider())
        task = Task(title=title, description=description)
        task.created_at = self.now_provider()  # deterministic when injected
        task.id = tid                           # keep object id == dict key
        self.tasks[tid] = task
        return tid

    def _require(self, task_id: str) -> Task:
        if task_id not in self.tasks:
            raise KeyError(task_id)
        return self.tasks[task_id]

    def edit(self, task_id: str, *, title: str | None = None, description: str | None = None) -> None:
        self._require(task_id).edit(title=title, description=description)

    def delete(self, task_id: str) -> None:
        self._require(task_id)
        del self.tasks[task_id]

    def complete(self, task_id: str) -> None:
        self._require(task_id).complete()

    def list(self) -> List[Tuple[str, Task]]:
        """
        Return (id, Task) pairs. Dicts preserve insertion order in Py3.7+,
        but you can sort here if you prefer by created_at or title.
        """
        return list(self.tasks.items())

    # ---------- Persistence (has I/O) ----------
    def save(self) -> None:
        """
        Atomic save:
          - ensure parent directory exists
          - write to a temp file in the same dir
          - os.replace(temp, final) to commit atomically
          - cleanup temp on any failure
        """
        directory = os.path.dirname(self.data_path) or "."
        os.makedirs(directory, exist_ok=True)

        fd, tmp_path = tempfile.mkstemp(prefix="tasks_", suffix=".json", dir=directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                payload = [dict(task.to_dict(), id=tid) for tid, task in self.tasks.items()]
                json.dump(payload, f, indent=2)
            os.replace(tmp_path, self.data_path)  # atomic on Windows/Unix
        except Exception:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except OSError:
                pass
            raise

    def load(self) -> None:
        """
        Safe load:
          - missing/empty file -> noop (empty tasks)
          - corrupt JSON -> raise DataLoadError
          - valid JSON -> rebuild tasks dict; keep ids consistent
        """
        path = self.data_path
        if not path or not os.path.exists(path) or os.path.getsize(path) == 0:
            self.tasks = {}
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise DataLoadError(f"Corrupt JSON at {path}") from e

        tasks: Dict[str, Task] = {}
        for rec in data:
            tid = rec.get("id")
            if not tid:
                continue  # or raise if you want strictness
            t = Task.from_dict(rec)
            t.id = tid
            tasks[tid] = t

        self.tasks = tasks

