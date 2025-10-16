# src/pipeline/cleaners.py
import pandas as pd

def clean_emails(df: pd.DataFrame, col: str = "email") -> pd.DataFrame:
    out = df.copy()
    if col in out:
        out[col] = out[col].astype(str).str.lower().str.strip()
    return out

def normalize_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize first/last names:
    - strip whitespace
    - lowercase then Capitalize
    - keep NaNs as NaN (don't turn into 'nan')
    """
    out = df.copy()

    def _norm(x):
        if pd.isna(x):
            return x
        s = str(x).strip()
        if not s:
            return s
        return s.lower().capitalize()

    for col in ("first_name", "last_name"):
        if col in out.columns:
            out[col] = out[col].map(_norm)

    return out

def add_signup_month(df: pd.DataFrame, date_col: str = "signup_date") -> pd.DataFrame:
    out = df.copy()
    if date_col in out:
        out[date_col] = pd.to_datetime(out[date_col], errors="coerce")
        out["signup_month"] = out[date_col].dt.to_period("M").astype(str)
    return out


# src/pipeline/cleaners.py
import pandas as pd

def clean_emails(df: pd.DataFrame, col: str = "email") -> pd.DataFrame:
    """
    Lowercase + strip email column (as string). Non-existent column is a no-op.
    NA handling follows pandas astype(str) behavior (e.g., '<NA>').
    """
    out = df.copy()
    if col in out.columns:
        out[col] = out[col].astype(str).str.lower().str.strip()
    return out

def normalize_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize first/last names:
    - strip whitespace
    - lowercase then capitalize first letter
    - keep NaNs as NaN (don't turn into 'nan' strings)
    """
    out = df.copy()

    def _norm(x):
        if pd.isna(x):
            return x
        s = str(x).strip()
        if not s:
            return s
        return s.lower().capitalize()

    for col in ("first_name", "last_name"):
        if col in out.columns:
            out[col] = out[col].map(_norm)

    return out

def add_signup_month(df: pd.DataFrame, date_col: str = "signup_date") -> pd.DataFrame:
    """
    Adds 'signup_month' as 'YYYY-MM' from a date column.
    Invalid dates -> NaT -> 'signup_month' becomes 'NaT' string for visibility.
    """
    out = df.copy()
    if date_col in out.columns:
        out[date_col] = pd.to_datetime(out[date_col], errors="coerce")
        # period('M') loses NaT; keep visibility by post-converting NaT to 'NaT'
        month = out[date_col].dt.to_period("M").astype("string")
        out["signup_month"] = month.fillna("NaT")
    return out
