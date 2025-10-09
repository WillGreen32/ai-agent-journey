"""TaskManager: manages collections of Task objects with CRUD + JSON persistence.

This module keeps persistence concerns (JSON read/write) close to the data model
without mixing user-interface concerns. The CLI is responsible for prompts and
error messages; the manager focuses on correctness and clear exceptions.
"""
from __future__ import annotations

import json
import os
from typing import List

from src.models.task import Task


class TaskManager:
    """Holds a list of Task objects and performs CRUD + JSON persistence."""

    def __init__(self) -> None:
        """Initialize an empty task list."""
        self.tasks: List[Task] = []

    # ---------- CRUD ----------
    def add_task(self, title: str) -> None:
        """Append a new task by title.

        Args:
            title (str): Human-readable task title.
        """
        self.tasks.append(Task(title=title))

    def edit_task(self, index: int, new_title: str) -> None:
        """Rename a task at the given zero-based index.

        Args:
            index (int): Zero-based index of the task to edit.
            new_title (str): Replacement title.

        Raises:
            IndexError: If index is out of range.
        """
        # Let the natural IndexError propagate if the index is invalid.
        self.tasks[index].title = new_title.strip()

    def delete_task(self, index: int) -> None:
        """Remove a task at the given zero-based index.

        Args:
            index (int): Zero-based index of the task to delete.

        Raises:
            IndexError: If index is out of range.
        """
        # Natural IndexError propagation on invalid indices.
        del self.tasks[index]

    # ---------- View ----------
    def view_tasks(self) -> None:
        """Print all tasks to the console in a numbered, readable list."""
        if not self.tasks:
            print("No tasks yet.")
            return
        print("\nYour Tasks:")
        for i, t in enumerate(self.tasks, start=1):
            print(f"{i}. {t.to_display()}")

    # ---------- Persistence ----------
    def save(self, path: str) -> None:
        """Write all tasks to a JSON file (UTF-8, pretty).

        Args:
            path (str): Destination file path (e.g., 'data/tasks.json').
        """
        # Ensure parent directory exists (safe when path includes a folder).
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in self.tasks], f, indent=2)

    def load(self, path: str) -> None:
        """Load tasks from a JSON file (UTF-8). Handles empty files gracefully.

        Args:
            path (str): Source file path.

        Notes:
            - If the file does not exist, this is a no-op.
            - If the file is present but empty, tasks remain an empty list.
            - If the file is corrupted (invalid JSON), this will raise a
              json.JSONDecodeError; allow the caller to handle/report it.
        """
        if not os.path.exists(path):
            return

        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                self.tasks = []
                return
            data = json.loads(content)

        self.tasks = [Task.from_dict(d) for d in data]
