from src.validate.errors import ValidationIssue
from src.validate.collector import IssueCollector
from src.validate.reporting import write_reports
from pathlib import Path
import json, csv

def test_report_files(tmp_path: Path):
    c = IssueCollector()
    c.add(ValidationIssue(row=1, field="id", code="duplicate", message="duplicate id A004"))
    paths = write_reports(c, tmp_path)
    assert Path(paths["csv"]).exists() and Path(paths["json"]).exists()
    # Spot check JSON contents
    data = json.loads(Path(paths["json"]).read_text(encoding="utf-8"))
    assert data[0]["code"] == "duplicate"
