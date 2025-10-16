from src.pipeline import cleaners

def test_email_lowercase(sample_df):
    df = cleaners.clean_emails(sample_df.copy())
    assert df["email"].str.islower().all()

def test_add_signup_month(sample_df):
    df = cleaners.add_signup_month(sample_df.copy())
    assert "signup_month" in df.columns
    assert set(df["signup_month"]) == {"2024-01", "2024-02"}

def test_sanity_check():
    assert True


import pandas as pd
import pytest
from src.pipeline import cleaners

def test_email_lowercase(sample_df):
    df = cleaners.clean_emails(sample_df.copy())
    assert df["email"].str.islower().all()

def test_add_signup_month(sample_df):
    df = cleaners.add_signup_month(sample_df.copy())
    assert "signup_month" in df.columns
    # From sample_df: 2024-01-10, 2024-02-02, 2024-01-31
    assert set(df["signup_month"]) == {"2024-01", "2024-02"}

# ---- Extra edge cases ----

@pytest.mark.parametrize("raw,expected", [
    ("  USER@ExAmPlE.COM  ", "user@example.com"),
    ("MixedCase@Domain.CoM", "mixedcase@domain.com"),
    (None, "none"),               # current impl uses astype(str) -> "None" or "nan"
    (pd.NA, "<NA>"),              # note: astype(str) on pandas NA -> "<NA>" (pandas 2.x)
])
def test_clean_emails_edge(raw, expected):
    df = pd.DataFrame({"email": [raw]})
    out = cleaners.clean_emails(df, "email")
    assert out.loc[0, "email"] == str(expected).lower().strip()

@pytest.mark.parametrize("raw_date,expected_month", [
    ("2024-02-29", "2024-02"),   # leap day
    ("2024/03/01", "2024-03"),   # different format
    ("not-a-date", "NaT"),       # coerced to NaT
    ("", "NaT"),                 # empty -> NaT
])
def test_add_signup_month_edge(raw_date, expected_month):
    df = pd.DataFrame({"signup_date": [raw_date]})
    out = cleaners.add_signup_month(df)
    # If coercion fails, month becomes "NaT"
    got = out.loc[0, "signup_month"]
    assert got == expected_month
