# super_break_fix.py

from __future__ import annotations
from datetime import date

# ----- Base -----
class Employee:
    def __init__(self, name: str, eid: int, start: date | None = None):
        self.name = name
        self.eid = eid
        self.start = start or date.today()

    def describe(self) -> str:
        return f"{self.name} (#{self.eid})"

# ----- BROKEN CHILD (no super in __init__) -----
class ManagerNoSuper(Employee):
    def __init__(self, name: str, eid: int, team=None):
        # ❌ Forgot super().__init__(...)
        self.team = list(team or [])

    def describe(self) -> str:
        # Will crash: base never created self.name / self.eid
        base = super().describe()
        return f"{base} — manages {len(self.team)}"

print("\n--- Drill A: Break it ---")
try:
    m_bad = ManagerNoSuper("Dylan", 201, team=[])
    print(m_bad.describe())
except Exception as e:
    print("Expected failure:", type(e).__name__, "-", e)

# ----- FIXED CHILD (uses super) -----
class Manager(Employee):
    def __init__(self, name: str, eid: int, team=None):
        super().__init__(name, eid)          # ✅ keep base attributes alive
        self.team = list(team or [])

    def describe(self) -> str:
        base = super().describe()             # ✅ extend base behavior
        return f"{base} — manages {len(self.team)}"

print("\n--- Drill A: Fix it ---")
m_ok = Manager("Dylan", 201, team=["Alice", "Bob"])
print(m_ok.describe())    # Dylan (#201) — manages 2
# ===== Drill B: Cooperative multiple inheritance =====

print("\n--- Drill B: Mixins + MRO ---")

class LoggingMixin:
    def __init__(self, *args, **kwargs):
        print("LoggingMixin.__init__")
        super().__init__(*args, **kwargs)
        self.logs = ["logging ready"]

class ComplianceMixin:
    def __init__(self, *args, **kwargs):
        print("ComplianceMixin.__init__")
        super().__init__(*args, **kwargs)
        self.compliance_id = "C-001"

class BaseService:
    def __init__(self, *args, **kwargs):
        print("BaseService.__init__")
        super().__init__(*args, **kwargs)
        self.base_ready = True

# ----- BROKEN: calls a specific parent, not super() -----
class OpsManagerBroken(LoggingMixin, ComplianceMixin, BaseService, Manager):
    def __init__(self, name: str, eid: int):
        print("OpsManagerBroken.__init__")
        # ❌ Wrong: direct parent call skips others in MRO
        Manager.__init__(self, name, eid, team=[])   # this **bypasses** Compliance/Logging/Base

print("MRO (Broken):", [c.__name__ for c in OpsManagerBroken.mro()])

try:
    ob = OpsManagerBroken("Nora", 301)
    # These will crash or be missing because __init__ chain was broken.
    print("logs:", ob.logs)
    print("compliance_id:", ob.compliance_id)
    print("base_ready:", ob.base_ready)
except Exception as e:
    print("Expected failure (broken chain):", type(e).__name__, "-", e)

# ----- FIXED: cooperative super everywhere -----
class OpsManager(LoggingMixin, ComplianceMixin, BaseService, Manager):
    def __init__(self, name: str, eid: int):
        print("OpsManager.__init__")
        super().__init__(name, eid, team=[])   # ✅ walks MRO: Manager -> BaseService -> Compliance -> Logging

print("MRO (Fixed):", [c.__name__ for c in OpsManager.mro()])

om = OpsManager("Nora", 301)
print("logs:", om.logs)                    # ['logging ready']
print("compliance_id:", om.compliance_id)  # 'C-001'
print("base_ready:", om.base_ready)        # True
print("describe:", om.describe())          # Dylan-style string with headcount
