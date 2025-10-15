import pandas as pd
from pathlib import Path

def transform_data(input_path: str, output_path: str) -> None:
    if input_path.endswith(".json"):
        df = pd.read_json(input_path, lines=True)
    else:
        df = pd.read_csv(input_path)

    if {"first_name","last_name"}.issubset(df.columns):
        df["full_name"] = (df["first_name"].fillna("") + " " + df["last_name"].fillna("")).str.strip()
    if "email" in df.columns:
        df["is_valid_email"] = df["email"].astype(str).str.contains(r"@.+\.", na=False)
    if "signup_date" in df.columns:
        df["signup_month"] = pd.to_datetime(df["signup_date"], errors="coerce").dt.month

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Transformed -> {output_path}")
