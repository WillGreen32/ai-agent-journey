import pandas as pd
from pathlib import Path

def export_data(input_path: str, report_path: str) -> None:
    df = pd.read_csv(input_path)
    if "state" not in df.columns:
        df["state"] = "UNKNOWN"

    out = df.groupby("state").agg(
        total_users=("user_id","count") if "user_id" in df.columns else ("state","count"),
        invalid_email_rate=("is_valid_email", lambda x: 1 - x.mean()) if "is_valid_email" in df.columns else ("state", lambda x: 0),
        duplicates=("email", lambda x: x.duplicated().sum()) if "email" in df.columns else ("state", lambda x: 0)
    ).reset_index()

    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(report_path, index=False)
    print(f"✅ Report saved -> {report_path}")
