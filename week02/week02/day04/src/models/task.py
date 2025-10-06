# src/models/task.py
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Task:
    """Represents a single to-do task with a title, timestamp, and done flag."""

    title: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    done: bool = False

    def mark_done(self):
        """Mark this task as complete."""
        self.done = True

    def to_display(self) -> str:
        """Return a nice printable version for the CLI."""
        symbol = "✓" if self.done else "•"
        return f"{symbol} {self.title}  ({self.created_at:%Y-%m-%d %H:%M})"

