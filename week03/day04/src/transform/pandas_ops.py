# week03/day04/src/transform/pandas_ops.py
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

# ---------------- Data contract ----------------
REQUIRED_COLS = ["user_id", "first_name", "last_name", "email", "signup_date", "state"]


def project_base() -> Path:
    """Return .../week03/day04 regardless of CWD."""
    return Path(__file__).resolve().parents[2]


# ---------------- Block 1: Loader ----------------
def load_input(input_path: str) -> pd.DataFrame:
    base = project_base()
    fp = base / input_path
    if not fp.exists():
        raise FileNotFoundError(f"Input file not found: {fp}")

    df = pd.read_csv(
        fp,
        dtype={
            "user_id": "Int64",
            "first_name": "string",
            "last_name": "string",
            "email": "string",
            "state": "string",
        },
        parse_dates=["signup_date"],
        keep_default_na=True,
        encoding="utf-8",
    )
    df.rename(columns=lambda c: c.strip(), inplace=True)

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise KeyError(
            f"Missing required columns: {missing}\nPresent: {list(df.columns)}"
        )
    return df


# ---------------- Block 2: Transform ----------------
def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Features
    df["full_name"] = (df["first_name"].fillna("") + " " + df["last_name"].fillna("")).str.strip()
    df["is_valid_email"] = df["email"].str.contains(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", na=False
    )
    df["signup_month"] = pd.to_datetime(df["signup_date"], errors="coerce").dt.month

    # State normalization
    df["state"] = df["state"].str.strip().str.upper()
    state_map = {
        "NEW SOUTH WALES": "NSW",
        "N.S.W.": "NSW",
        "VICTORIA": "VIC",
        "QUEENSLAND": "QLD",
        "SOUTH AUSTRALIA": "SA",
        "WESTERN AUSTRALIA": "WA",
        "TASMANIA": "TAS",
        "NORTHERN TERRITORY": "NT",
        "AUSTRALIAN CAPITAL TERRITORY": "ACT",
    }
    df["state"] = df["state"].replace(state_map)

    # Null normalization
    df.replace({"": pd.NA, "UNKNOWN": pd.NA, "NONE": pd.NA, "null": pd.NA, "Null": pd.NA}, inplace=True)
    df["email"] = df["email"].fillna("unknown@example.com")
    df = df.dropna(subset=["state"])

    # Duplicates
    # Normalize case/whitespace before duplicate detection (more realistic)
    df["email_norm"] = df["email"].str.strip().str.lower()
    df["email_is_duplicate"] = df["email_norm"].duplicated(keep=False)

    _post_transform_assertions(df)
    return df


def _post_transform_assertions(df: pd.DataFrame) -> None:
    bad = df.loc[
        ~df["signup_month"].isin([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        & df["signup_month"].notna()
    ]
    if not bad.empty:
        raise AssertionError("Invalid signup_month values present.")

    if df["state"].isna().any():
        raise AssertionError("Null states remain after cleaning.")

    expected = {"full_name", "is_valid_email", "signup_month", "email_is_duplicate", "email_norm"}
    missing = expected - set(df.columns)
    if missing:
        raise AssertionError(f"Missing expected transform columns: {missing}")


# ---------------- Block 3: Aggregate + Export + CLI ----------------
def _month_columns_present(months: Iterable[int]) -> list[str]:
    """Generate consistent month column names m1_users..m12_users (only for months present)."""
    return [f"m{int(m)}_users" for m in months]


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    # Core KPIs
    agg = df.groupby("state", as_index=False).agg(
        total_users=("user_id", "count"),
        invalid_email_rate=("is_valid_email", lambda x: float(1 - x.mean()) if len(x) else 0.0),
        duplicates=("email_norm", lambda s: int(s.duplicated().sum())),
    )

    # Monthly counts per state (wide)
    monthly = df.pivot_table(
        index="state",
        columns="signup_month",
        values="user_id",
        aggfunc="count",
        fill_value=0,
    )
    # Keep months in natural order, convert to m{n}_users naming
    months_present = sorted([c for c in monthly.columns if pd.notna(c)])
    monthly.columns = _month_columns_present(months_present)
    monthly = monthly.reset_index()

    # Merge
    out = agg.merge(monthly, on="state", how="left")

    # Sort for readability
    out = out.sort_values(["state"]).reset_index(drop=True)

    # Nice rounding for rates
    if "invalid_email_rate" in out.columns:
        out["invalid_email_rate"] = out["invalid_email_rate"].round(4)

    return out


def save_report(df_out: pd.DataFrame, out_path: str) -> None:
    base = project_base()
    fp = base / out_path
    fp.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(fp, index=False)
    print(f"✅ Saved {fp}")


def build_cli() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Pandas transform + aggregate pipeline")
    p.add_argument("--input", default="data/processed_users.csv", help="Input CSV path (relative to week03/day04)")
    p.add_argument("--output", default="reports/quality_dashboard.csv", help="Output CSV path")
    return p


def main():
    args = build_cli().parse_args()
    df = load_input(args.input)
    df = transform(df)
    out = aggregate(df)

    # basic quality assertions
    required_out = {"state", "total_users", "invalid_email_rate", "duplicates"}
    assert required_out.issubset(out.columns), f"Missing expected columns in output: {required_out - set(out.columns)}"

    save_report(out, args.output)


if __name__ == "__main__":
    main()
