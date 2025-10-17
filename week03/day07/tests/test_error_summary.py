from src.validate.errors import ValidationIssue
from src.validate.collector import IssueCollector
from src.validate.reporting import print_summary
from io import StringIO
import sys

def test_summary_formats_examples(capsys):
    c = IssueCollector()
    c.add(ValidationIssue(row=12, field="email", code="missing_field", message="missing 'email'"))
    c.add(ValidationIssue(row=28, field="state", code="invalid_state", message="invalid state 'WAH'"))
    print_summary(c, show_examples=2)
    out = capsys.readouterr().out
    assert "Validation failed" in out and "Row 12" in out and "Row 28" in out
