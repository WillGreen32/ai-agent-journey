from __future__ import annotations
from datetime import date
from typing import Iterable, List

# ---- RUN TOGGLES ----
RUN_NEGATIVE_TEST = True         # show BadManager failure
SET_COMPANY_TO_GLOBAL = False    # flip True if you want "Acme Global"
RUN_FINAL_ASSERTS = True         # final sanity checks
# ----------------------


class Employee:
    """Base employee with required state + simple behavior."""

    company = "Acme Corp"  # class attribute

    def __init__(self, name: str, eid: int, role: str, start_date: date | None = None):
        if not self._valid_name(name):
            raise ValueError("name must be a non-empty string")
        if not self._valid_eid(eid):
            raise ValueError("eid must be a positive integer")
        if not self._valid_name(role):
            raise ValueError("role must be a non-empty string")

        self.name = name
        self.eid = eid
        self.role = role
        self.start_date = start_date or date.today()
        self._notes: List[str] = []  # private-ish convention

    # -------- instance behavior
    def tenure_years(self) -> float:
        days = (date.today() - self.start_date).days
        return round(days / 365.25, 2)

    def add_note(self, text: str) -> None:
        if not self._valid_name(text):
            raise ValueError("note must be non-empty")
        self._notes.append(text)

    def notes(self) -> tuple[str, ...]:
        # expose as immutable
        return tuple(self._notes)

    def describe(self) -> str:
        return f"{self.name} (#{self.eid}) — {self.role} @ {self.company}"

    # -------- class/staticmethods
    @classmethod
    def set_company(cls, name: str) -> None:
        if not cls._valid_name(name):
            raise ValueError("company must be non-empty")
        cls.company = name

    @staticmethod
    def _valid_name(s) -> bool:
        return isinstance(s, str) and s.strip() != ""

    @staticmethod
    def _valid_eid(e) -> bool:
        return isinstance(e, int) and e > 0

    def __repr__(self) -> str:
        return f"Employee(name={self.name!r}, eid={self.eid}, role={self.role!r})"


class Manager(Employee):
    """Manager extends Employee: adds team, headcount ops, overrides describe()."""

    def __init__(self, name: str, eid: int, role: str = "Manager",
                 start_date: date | None = None, team: Iterable[Employee] | None = None):
        # Keep base attributes alive
        super().__init__(name, eid, role, start_date)
        # Manager-specific state
        self.team: list[Employee] = list(team or [])

    # ---- manager behavior
    def headcount(self) -> int:
        return len(self.team)

    def add_report(self, emp: Employee) -> None:
        if not isinstance(emp, Employee):
            raise TypeError("emp must be an Employee")
        if emp is self:
            raise ValueError("manager cannot add themselves as a report")
        if emp in self.team:
            return  # idempotent
        self.team.append(emp)

    def remove_report(self, emp: Employee) -> None:
        if emp in self.team:
            self.team.remove(emp)

    def list_reports(self) -> list[str]:
        return [f"{e.name} (#{e.eid}) — {e.role}" for e in self.team]

    # ---- override: extend base description
    def describe(self) -> str:
        base = super().describe()
        return f"{base} — manages {self.headcount()}"

    # ---- small convenience
    def transfer_team_to(self, other: "Manager") -> None:
        if not isinstance(other, Manager):
            raise TypeError("other must be a Manager")
        for emp in list(self.team):
            other.add_report(emp)
            self.remove_report(emp)
class BadManager(Employee):
    def __init__(self, name: str, eid: int):
        # no super().__init__(...)  -> base state not created
        self.team = []

    def describe(self) -> str:
        # will crash: parent fields not set
        return f"{self.name} (#{self.eid}) — {self.role} @ {self.company}"

# In __main__ (temporarily):
    try:
        bm = BadManager("Zoe", 999)
        print(bm.describe())
    except Exception as exc:
        print("Expected failure (no super in __init__):", type(exc).__name__, "-", exc)

            

if __name__ == "__main__":
    # Optional: set the class attribute on both Employee/Manager via classmethod
    if SET_COMPANY_TO_GLOBAL:
        Manager.set_company("Acme Global")

    # ---------- Negative test isolated ----------
    if RUN_NEGATIVE_TEST:
        print("\n-- Negative Test: BadManager without super() --")
        try:
            bm = BadManager("Zoe", 999)
            print(bm.describe())  # should crash
        except Exception as exc:
            print("Expected failure (no super in __init__):", type(exc).__name__, "-", exc)

    print("\n-- Normal Demo / Quick Checks --")
    e1 = Employee("Alice", 101, "Developer")
    e2 = Employee("Bob", 102, "Analyst")
    e3 = Employee("Cara", 103, "Designer")

    m = Manager("Dylan", 201, team=[e1, e2])
    print(m.describe())
    print("Reports:", m.list_reports())
    m.add_report(e3)
    print("Headcount after add:", m.headcount())
    m.remove_report(e2)
    print("Headcount after remove:", m.headcount())

    print("Company:", Employee.company, "|", Manager.company)

    # Polymorphism
    staff: list[Employee] = [e1, e2, e3, m]
    for s in staff:
        print("->", s.describe())

    # ---- Final asserts (safe) ----
    if RUN_FINAL_ASSERTS:
        # Don’t hardcode the string; just ensure they MATCH
        assert Employee.company == Manager.company, "Employee.company and Manager.company should match"
        assert isinstance(m, Manager) and isinstance(m, Employee)
        assert "manages" in m.describe()
        print("Assertions passed.")
