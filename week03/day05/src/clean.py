import pandas as pd
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df = df.drop_duplicates()
    if "email" in df.columns:
        df["email"] = df["email"].fillna("unknown@example.com")
    return df
