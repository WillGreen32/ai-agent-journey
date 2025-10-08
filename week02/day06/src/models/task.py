from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

TITLE_MAX_LEN = 120


@dataclass
class Task:
    title: str
    description: str = ""
    completed: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        t = (self.title or "").strip()
        if not t:
            raise ValueError("Title cannot be empty")
        if len(t) > TITLE_MAX_LEN:
            raise ValueError(f"Title exceeds {TITLE_MAX_LEN} chars")
        self.title = t  # normalize

    def complete(self) -> None:
        self.completed = True

    def edit(self, title: str | None = None, description: str | None = None) -> None:
        # Title rules
        if title is not None:
            t = title.strip()
            if not t:
                raise ValueError("Title cannot be empty")
            if len(t) > TITLE_MAX_LEN:
                raise ValueError(f"Title exceeds {TITLE_MAX_LEN} chars")
            self.title = t
        # Description rules
        if description is not None:
            self.description = description

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat(),  # tz-aware ISO 8601
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Task":
        """
        Build a Task from a JSON-safe dict. Unknown keys are ignored.
        Required: title, created_at. If 'id' missing, a new one is generated.
        """
        obj = cls(
            title=d["title"],
            description=d.get("description", ""),
            completed=d.get("completed", False),
        )
        if "id" in d:
            obj.id = d["id"]
        obj.created_at = datetime.fromisoformat(d["created_at"])
        return obj
