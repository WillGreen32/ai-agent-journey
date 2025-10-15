import pandas as pd
from pathlib import Path

def validate_data(input_path: str, report_dir: str = "reports") -> None:
    Path(report_dir).mkdir(parents=True, exist_ok=True)
    if input_path.endswith(".json"):
        df = pd.read_json(input_path, lines=True)
    else:
        df = pd.read_csv(input_path)

    issues = []
    if "email" in df.columns:
        invalid_email = ~df["email"].astype(str).str.contains(r"@.+\.", na=False)
        if invalid_email.any():
            issues.append(f"Invalid emails: {invalid_email.sum()}")

    if "age" in df.columns:
        bad_age = ~df["age"].between(0, 120)
        if bad_age.any():
            issues.append(f"Out-of-range ages: {bad_age.sum()}")

    report_path = Path(report_dir) / "validation_report.txt"
    if issues:
        report_path.write_text("VALIDATION ISSUES:\n- " + "\n- ".join(issues))
        print(f"⚠️ Validation issues found. See {report_path}")
    else:
        report_path.write_text("All checks passed ✅")
        print(f"✅ Validation passed. See {report_path}")
