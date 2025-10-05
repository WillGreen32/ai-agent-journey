# src/task.py
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

@dataclass
class Task:
    title: str
    due: Optional[datetime] = None
    priority: int = 3
    done: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

    def mark_done(self) -> None:
        self.done = True

    def is_overdue(self) -> bool:
        return (self.due is not None) and (not self.done) and (datetime.utcnow() > self.due)

    def __repr__(self) -> str:
        status = "✓" if self.done else "•"
        return f"<{status} {self.title} p{self.priority} due={self.due}>"

class UrgentTask(Task):
    def __init__(self, title: str, hours: int = 24):
        super().__init__(title=title, due=datetime.utcnow() + timedelta(hours=hours), priority=1)

class RecurringTask(Task):
    def __init__(self, title: str, interval_days: int = 7):
        super().__init__(title=title)
        self.interval_days = interval_days

    def complete_and_schedule_next(self) -> "RecurringTask":
        self.mark_done()
        return RecurringTask(title=self.title, interval_days=self.interval_days)

    def next_due(self) -> datetime:
        base = self.due or datetime.utcnow()
        return base + timedelta(days=self.interval_days)

class CompletedTask(Task):
    def __init__(self, title: str):
        super().__init__(title=title, done=True)
