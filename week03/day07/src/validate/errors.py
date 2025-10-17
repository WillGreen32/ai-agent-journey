from dataclasses import dataclass
from typing import Optional, Literal

Severity = Literal["error", "warning"]

@dataclass(frozen=True)
class ValidationIssue:
    row: Optional[int]          # None for global issues
    field: Optional[str]        # e.g., "email"
    code: str                   # e.g., "missing_field", "invalid_state"
    message: str                # human-friendly text
    severity: Severity = "error"
