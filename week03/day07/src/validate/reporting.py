from pathlib import Path
from typing import Optional
import csv, json, sys
from .collector import IssueCollector

def print_summary(collector: IssueCollector, show_examples:int=5) -> None:
    counts = collector.counts()
    total = counts["errors"] + counts["warnings"]
    if total == 0:
        print("✅ Validation passed.")
        return
    head = f"❌ Validation failed ({total} issue{'s' if total!=1 else ''} | " \
           f"{counts['errors']} error(s), {counts['warnings']} warning(s))"
    print(head)
    for line in collector.group_examples(limit=show_examples):
        print(line)
    if total > show_examples:
        remaining = total - show_examples
        print(f"   … and {remaining} more.")


def write_reports(collector: IssueCollector, out_dir: Path, basename:str="validation_report") -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    # CSV
    csv_path = out_dir / f"{basename}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["row","field","code","message","severity"])
        for i in collector.issues:
            w.writerow([i.row, i.field, i.code, i.message, i.severity])
    # JSON
    json_path = out_dir / f"{basename}.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump([i.__dict__ for i in collector.issues], f, ensure_ascii=False, indent=2)
    return {"csv": csv_path, "json": json_path}


def exit_for_issues(collector: IssueCollector, success_code:int=0, error_code:int=1) -> None:
    if collector.is_fatal():
        sys.exit(error_code)
    sys.exit(success_code)
