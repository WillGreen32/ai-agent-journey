from src.io.reader import read_csv, write_csv
from src.clean.clean_data import clean_dataframe
from src.validate.validator import validate_rows
from src.transform.transform_data import transform_dataframe

# src/validate/validator.py (example fragments)
from src.validate.errors import ValidationIssue

def check_required(df, required_fields):
    for f in required_fields:
        missing = df[df[f].isna()].index.tolist() if f in df.columns else df.index.tolist()
        for idx in missing:
            yield ValidationIssue(row=int(idx)+2, field=f, code="missing_field",
                                  message=f"missing '{f}'", severity="error")  # +2 for header + 1-index

def check_state(df, allowed):
    if "state" not in df.columns: return
    bad = ~df["state"].isin(allowed)
    for idx, val in df.loc[bad,"state"].items():
        yield ValidationIssue(row=int(idx)+2, field="state", code="invalid_state",
                              message=f"invalid state '{val}' (allowed: {', '.join(allowed)})",
                              severity="error")
