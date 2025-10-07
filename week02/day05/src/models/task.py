# src/models/task.py
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class Task:
    title: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    done: bool = False

    # Normalize + validate
    def __post_init__(self) -> None:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("Task.title cannot be empty")

        # Make sure created_at is timezone-aware (UTC)
        if self.created_at.tzinfo is None or self.created_at.tzinfo.utcoffset(self.created_at) is None:
            # Coerce naive datetimes to UTC to avoid later surprises
            self.created_at = self.created_at.replace(tzinfo=timezone.utc)

    # Pretty display for CLI
    def __str__(self) -> str:
        mark = "✓" if self.done else "•"
        return f"{mark} {self.title}"

    # JSON-safe serialization
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "created_at": self.created_at.isoformat(),  # ISO-8601 string with timezone
            "done": self.done,
        }

    # Tolerant deserialization
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """
        Build Task from a JSON dict. Tolerant of missing/invalid fields:
        - missing/invalid created_at -> now(UTC)
        - missing done -> False
        - title must be non-empty post-strip (ValueError if empty)
        """
        raw_title = (data.get("title") or "").strip()
        if not raw_title:
            raise ValueError("Missing/empty title during load")

        raw_ts = data.get("created_at")
        try:
            created = datetime.fromisoformat(raw_ts) if isinstance(raw_ts, str) else None
        except Exception:
            created = None
        if created is None:
            created = datetime.now(timezone.utc)
        # Coerce naive -> UTC
        if created.tzinfo is None or created.tzinfo.utcoffset(created) is None:
            created = created.replace(tzinfo=timezone.utc)

        done = bool(data.get("done", False))
        return cls(title=raw_title, created_at=created, done=done)


