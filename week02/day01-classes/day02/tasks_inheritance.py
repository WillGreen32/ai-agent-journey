"""Day 2 — Task system: inheritance, overriding, super()

File: tasks_inheritance.py
Goal: Build a mini task system to practice:
- Base → Children inheritance
- Method overriding
- Proper use of super() to keep parent behavior alive

Run:
    python tasks_inheritance.py
"""

from __future__ import annotations
from enum import Enum
from typing import Union


# ---------- Strongly-typed status ----------
class Status(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    URGENT = "urgent"   # reserved for UrgentTask


# ---------- Base: Task ----------
class Task:
    """
    Robust base Task with:
      - input validation (title/description non-empty)
      - typed status via Enum (but accepts strings)
      - safe state transitions (single source of truth)
      - convenience API: start/complete/reset/mark_urgent
    Subclasses should call super().__init__(...) to keep invariants alive.
    """

    # Allowed transitions (explicit state machine)
    _ALLOWED_NEXT = {
        Status.PENDING: {Status.IN_PROGRESS, Status.URGENT, Status.COMPLETED},
        Status.IN_PROGRESS: {Status.PENDING, Status.COMPLETED, Status.URGENT},
        Status.URGENT: {Status.IN_PROGRESS, Status.COMPLETED},     # no direct -> pending
        Status.COMPLETED: {Status.PENDING},                        # allow reset after completion
    }

    def __init__(self, title: str, description: str, status: Union[Status, str] = Status.PENDING):
        # ---- validate inputs
        if not self._nonempty(title):
            raise ValueError("title must be a non-empty string")
        if not self._nonempty(description):
            raise ValueError("description must be a non-empty string")

        # ---- coerce/validate status
        self.title = title.strip()
        self.description = description.strip()
        self.status = self._coerce_status(status)

        # ---- ensure initial status is legal
        if self.status not in {
            Status.PENDING, Status.IN_PROGRESS, Status.COMPLETED, Status.URGENT
        }:
            raise ValueError(f"Unsupported initial status: {self.status!r}")

    # ===== Public API (nice verbs) =====
    def start(self) -> None:
        """Move to in_progress unless completed (use reset() first if needed)."""
        self._transition_to(Status.IN_PROGRESS)

    def complete(self) -> None:
        """Mark as completed."""
        self._transition_to(Status.COMPLETED)

    def reset(self) -> None:
        """Reset back to pending (allowed even from completed)."""
        self._transition_to(Status.PENDING)

    def mark_urgent(self) -> None:
        """Mark as urgent (base implementation; UrgentTask will override/enhance)."""
        self._transition_to(Status.URGENT)

    # ===== Core transition logic =====
    def _transition_to(self, next_status: Status) -> None:
        current = self.status
        allowed = self._ALLOWED_NEXT.get(current, set())
        if next_status not in allowed:
            raise ValueError(
                f"Illegal transition: {current.value} -> {next_status.value}. "
                f"Allowed: {[s.value for s in allowed]}"
            )
        self.status = next_status

    # ===== Utilities =====
    @staticmethod
    def _nonempty(s: object) -> bool:
        return isinstance(s, str) and s.strip() != ""

    @staticmethod
    def _coerce_status(s: Union[Status, str]) -> Status:
        if isinstance(s, Status):
            return s
        if isinstance(s, str):
            s = s.strip().lower()
            return Status(s)  # raises ValueError automatically if unknown
        raise TypeError("status must be a Status or str")

    # ===== Display / debugging =====
    def __str__(self) -> str:
        return f"[{self.status.value}] {self.title}: {self.description}"

    def __repr__(self) -> str:
        return f"Task(title={self.title!r}, status={self.status.value!r})"

    # ===== Optional helper =====
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Tiny constructor for factories/imports."""
        return cls(
            title=data["title"],
            description=data.get("description", ""),
            status=data.get("status", Status.PENDING),
        )


# ---------- UrgentTask (child of Task) ----------
class UrgentTask(Task):
    """
    - Always starts with status = "urgent"
    - Adds priority_level (int)
    - escalate() to bump priority
    - Overrides __str__ for special formatting
    """
    def __init__(self, title: str, description: str, priority_level: int):
        super().__init__(title, description, status=Status.URGENT)
        self.priority_level = int(priority_level)

    def escalate(self) -> None:
        self.priority_level += 1

    def complete(self) -> None:
        # Keep base behavior (state machine, etc.)
        super().complete()

    def __str__(self) -> str:
        return f"[URGENT-{self.priority_level}] {self.title}: {self.description}"

# ---------- RecurringTask ----------
class RecurringTask(Task):
    """
    A Task that auto-resets to pending after being completed,
    simulating repeated occurrences (daily, weekly, etc.).
    """

    _ALLOWED_FREQ = {"daily", "weekly", "monthly", "yearly"}

    def __init__(self, title: str, description: str, frequency: str):
        # Always start at pending for a new cycle
        super().__init__(title, description, status=Status.PENDING)

        # Normalize + validate frequency
        if not isinstance(frequency, str) or not frequency.strip():
            raise ValueError("frequency must be a non-empty string")
        freq = frequency.strip().lower()
        if freq not in self._ALLOWED_FREQ:
            raise ValueError(f"frequency must be one of {sorted(self._ALLOWED_FREQ)}, got {frequency!r}")
        self.frequency = freq

        # Optional tracking (nice for analytics / UI badges)
        self.occurrence_count = 0          # how many completions done
        self.last_completed_at = None      # timestamp of last run (can remain None until first completion)

    def complete(self) -> None:
        """
        Extend base completion:
        1) Mark this occurrence completed (keeps parent invariants/transition rules)
        2) Increment occurrence metrics
        3) Immediately get ready for the next run (reset to pending)
        """
        # 1) Mark completed (enforces allowed transition)
        super().complete()

        # 2) Update counters / timestamp
        self.occurrence_count += 1
        from datetime import datetime
        self.last_completed_at = datetime.now()

        # 3) Prepare next occurrence: completed -> pending is allowed by your base table
        self.reset()

    def __str__(self) -> str:
        # Show frequency and current status; include count if >0
        suffix = f" (done {self.occurrence_count}x)" if self.occurrence_count else ""
        return f"[RECUR-{self.frequency}] {self.title}: {self.description} ({self.status.value}){suffix}"

# ---------- CompletedTask (locked) ----------
class CompletedTask(Task):
    """
    Immutable Task: constructed as completed and cannot be restarted, reset, or re-urgent'ed.
    """

    def __init__(self, title: str, description: str, date_completed: str):
        # Force completed status but still run the base validations/invariants
        super().__init__(title, description, status=Status.COMPLETED)

        # Keep date simple as string for now; you can switch to datetime later
        if not isinstance(date_completed, str) or not date_completed.strip():
            raise ValueError("date_completed must be a non-empty string like '2025-10-01'")
        self.date_completed = date_completed.strip()

    # ---- Block all state-changing operations ----
    def start(self) -> None:
        raise ValueError("CompletedTask is immutable")

    def reset(self) -> None:
        raise ValueError("CompletedTask is immutable")

    def mark_urgent(self) -> None:
        raise ValueError("CompletedTask is immutable")

    def complete(self) -> None:
        # Already complete; do nothing (or raise if you prefer)
        return

    def __str__(self) -> str:
        return f"[DONE {self.date_completed}] {self.title}: {self.description}"


# ---------- Sanity run ----------
if __name__ == "__main__":
    print("\n-- Base Task sanity --")
    t = Task("Write spec", "Draft module interface")
    print(t)                 # [pending] ...
    t.start(); print(t)      # [in_progress] ...
    t.mark_urgent(); print(t)# [urgent] ...
    t.complete(); print(t)   # [completed] ...
    t.reset(); print(t)      # [pending] ...

    print("\n-- UrgentTask sanity --")
    u = UrgentTask("Fix prod bug", "Error 500 on homepage", 2)
    print("Initial:", u)           # [URGENT-2] ...
    u.escalate(); print("Escalated:", u)  # [URGENT-3] ...
    u.complete();  print("Completed:", u) # status is completed (string still shows urgent header by design)

    # illegal transition demo: URGENT -> PENDING (not allowed directly)
    try:
        x = Task("Demo", "Illegal move demo", status=Status.URGENT)
        x.reset()  # raises by table (urgent->pending not allowed)
    except ValueError as e:
        print("Caught illegal transition:", e)
if __name__ == "__main__":
    print("\n-- UrgentTask sanity --")
    u = UrgentTask("Fix prod bug", "Error 500 on homepage", 2)
    print("Initial:", u)      # expect [URGENT-2] Fix prod bug: Error 500 on homepage
    u.escalate()
    print("After escalate:", u)  # [URGENT-3] ...
    u.complete()
    print("After complete:", u)  # status changes to completed, but __str__ still shows urgent format

    print("\n-- RecurringTask sanity --")
    rec = RecurringTask("Weekly report", "Email metrics to stakeholders", "weekly")
    print("Before:", rec)               # [RECUR-weekly] ... (pending)
    rec.start(); print("Started:", rec) # [RECUR-weekly] ... (in_progress)
    rec.complete(); print("After complete (auto-reset):", rec)
    # Expect: status back to pending, occurrence_count incremented, last_completed_at set

    # Show repeated cycles work
    rec.complete(); print("After complete x2:", rec)
    rec.complete(); print("After complete x3:", rec)

    # Guards still apply: invalid frequency
    try:
        bad = RecurringTask("Bad", "Invalid freq", "every now and then")
    except Exception as e:
        print("Invalid frequency blocked →", type(e).__name__, "-", e)


# ---------- Polymorphism demo + assertions ----------
if __name__ == "__main__":
    print("\n-- Polymorphism demo --")
    items: list[Task] = [
        Task("Write brief", "Day 3 outline"),
        UrgentTask("Hotfix", "NullRef crash", 3),
        RecurringTask("Weekly report", "Email metrics", "weekly"),
        CompletedTask("Migrate DNS", "Cutover done", "2025-10-01"),
        WorkTask("Spec review", "API v2", "Alice"),
    ]

    for t in items:
        print(f"{type(t).__name__} -> {t}")

    # ---------- Behavior differences ----------
    print("\n-- Behavior checks --")

    # A) Recurring resets after completion
    rec = RecurringTask("Backup", "Nightly snapshot", "daily")
    print("Before:", rec)                 # pending
    rec.complete()
    print("After complete (auto-reset):", rec)  # pending again

    # B) CompletedTask should reject changes
    done = CompletedTask("Invoices", "September batch", "2025-10-01")
    try:
        done.start()
    except Exception as e:
        print("CompletedTask guard OK →", type(e).__name__)

    # C) WorkTask assign/unassign
    w = WorkTask("Code review", "PR #42")
    print("Unassigned:", w)
    w.assign("Bob"); print("Assigned:", w)
    w.unassign();   print("Unassigned again:", w)

    # D) Urgent escalation + completion
    u = UrgentTask("Pager alert", "DB latency", 1)
    print("Urgent:", u)
    u.escalate(); print("Escalated:", u)
    u.complete(); print("Completed urgent:", u)

    # ---------- Quick assertions (fast red/green) ----------
    # NOTE: You’re using a Status enum, so assert against Status, not raw strings.
    assert isinstance(u, Task)
    assert isinstance(done, Task) and done.status == Status.COMPLETED
    assert rec.status == Status.PENDING          # auto-reset put it back to pending
    assert "unassigned" in str(w)                # WorkTask string shows owner state
    print("\nAssertions passed.")
