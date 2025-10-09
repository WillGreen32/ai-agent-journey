"""Task model: defines the Task class and helpers for display and JSON persistence."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict


def _utcnow() -> datetime:
    """Return timezone-aware UTC now (safe for JSON round-trips)."""
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Task:
    """Represents a single to-do item with title, creation time (UTC), and completion state."""

    title: str
    created_at: datetime = field(default_factory=_utcnow)
    done: bool = False

    # ---------- Behavior ----------
    def mark_done(self) -> None:
        """Mark this task as completed."""
        self.done = True

    # ---------- Views / Presentation ----------
    def to_display(self) -> str:
        """Return a friendly string for CLI lists with local time rendering."""
        symbol = "✓" if self.done else "•"
        local_time = self.created_at.astimezone()  # convert UTC → local for display
        return f"{symbol} {self.title} ({local_time:%Y-%m-%d %H:%M})"

    # ---------- Persistence ----------
    def to_dict(self) -> Dict[str, Any]:
        """Serialize task to a JSON-safe dictionary using ISO 8601 timestamps."""
        return {
            "title": self.title,
            "created_at": self.created_at.isoformat(),  # e.g., '2025-10-09T12:34:56.789+00:00'
            "done": self.done,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Reconstruct a Task from a dictionary produced by to_dict().

        Args:
            data (dict): Keys 'title' (str), 'created_at' (ISO str), 'done' (bool).

        Returns:
            Task: Reconstructed Task instance.
        """
        ts = data.get("created_at")
        # Robust parsing: if timezone missing, assume UTC
        dt = datetime.fromisoformat(ts) if ts else _utcnow()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return cls(title=data.get("title", ""), created_at=dt, done=bool(data.get("done", False)))

    # ---------- Light validation / normalization ----------
    def __post_init__(self) -> None:
        """Normalize fields for consistency (strip title; coerce tz)."""
        self.title = (self.title or "").strip()
        if self.created_at.tzinfo is None:
            # Always maintain timezone-aware UTC for persistence correctness
            self.created_at = self.created_at.replace(tzinfo=timezone.utc)
