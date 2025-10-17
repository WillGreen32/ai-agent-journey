from collections import defaultdict, Counter
from typing import Iterable, List, Dict
from .errors import ValidationIssue

class IssueCollector:
    def __init__(self):
        self._issues: List[ValidationIssue] = []

    def add(self, issue: ValidationIssue) -> None:
        self._issues.append(issue)

    def extend(self, issues: Iterable[ValidationIssue]) -> None:
        self._issues.extend(list(issues))

    @property
    def issues(self) -> List[ValidationIssue]:
        return list(self._issues)

    def counts(self) -> Dict[str, int]:
        # Count by severity
        by_sev = Counter(i.severity for i in self._issues)
        return {"errors": by_sev.get("error", 0), "warnings": by_sev.get("warning", 0)}

    def is_fatal(self) -> bool:
        return any(i.severity == "error" for i in self._issues)

    def group_examples(self, limit:int=5) -> List[str]:
        lines = []
        for i in self._issues[:limit]:
            where = f"Row {i.row}" if i.row is not None else "Global"
            field = f" — {i.field}" if i.field else ""
            lines.append(f"   • {where}{field} — {i.message}")
        return lines
