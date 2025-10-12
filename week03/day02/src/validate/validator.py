# ---------- Coercion helpers (pure, side-effect free) ----------
from datetime import datetime
import math
import re

# Empty markers treated as "no value" (=> None before constraints)
EMPTY_MARKERS = (None, "")

# Optional normalization toggles (kept internal for now; you can expose via schema later)
_TRIM_WHITESPACE = True
_ALLOW_NUMERIC_COMMAS = True           # "1,234" -> 1234
_ALLOW_NUMERIC_UNDERSCORES = True      # "1_234" -> 1234
_ACCEPT_STRINGS_FOR_BOOL = True
_BOOL_TRUE = {"true", "1", "yes", "y", "on"}
_BOOL_FALSE = {"false", "0", "no", "n", "off"}

# Common alternative empties encountered in CSVs
_ALT_EMPTY_STRINGS = {"na", "n/a", "null", "none", "nil"}  # case-insensitive

# --- import shim so the file works whether run as a module or a script ---
try:
    from src.io.csv_io import load_csv
except ModuleNotFoundError:
    # When running the file directly, add the parent 'src' folder to sys.path
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parents[1]))  # -> .../src
    from io.csv_io import load_csv


def _normalize_raw(v):
    if v is None:
        return None
    s = str(v)
    if _TRIM_WHITESPACE:
        s = s.strip()
    # Treat common textual empties as None
    if s.lower() in _ALT_EMPTY_STRINGS or s == "":
        return None
    return s

def to_str(v):
    s = _normalize_raw(v)
    return None if s is None else s  # return trimmed string

def _strip_numeric_noise(s: str) -> str:
    if _ALLOW_NUMERIC_COMMAS:
        s = s.replace(",", "")
    if _ALLOW_NUMERIC_UNDERSCORES:
        s = s.replace("_", "")
    return s

def to_int(v):
    s = _normalize_raw(v)
    if s is None:
        return None
    s = _strip_numeric_noise(s)
    # Guard against floats pretending to be ints: "42.0" is invalid for int
    if re.search(r"[.\s]", s):
        raise ValueError(f"not an int: {v!r}")
    return int(s)

def to_float(v):
    s = _normalize_raw(v)
    if s is None:
        return None
    s = _strip_numeric_noise(s)
    # Reject non-numeric tokens like "inf" unless explicitly allowed
    if s.lower() in {"nan", "+nan", "-nan", "inf", "+inf", "-inf"}:
        raise ValueError(f"not a finite float: {v!r}")
    x = float(s)
    if not math.isfinite(x):
        raise ValueError(f"not a finite float: {v!r}")
    return x

def to_bool(v):
    if v is None:
        return None
    s = _normalize_raw(v)
    if s is None:
        return None
    s = s.lower()
    if s in _BOOL_TRUE:
        return True
    if s in _BOOL_FALSE:
        return False
    # Accept direct bools
    if isinstance(v, bool):
        return v
    raise ValueError(f"not a bool: {v!r}")

def to_date(v, fmt="%Y-%m-%d", try_formats=None):
    """
    Coerce to date; primary format first, then fallback formats if provided.
    - fmt: primary format
    - try_formats: optional list of fallback formats
    """
    s = _normalize_raw(v)
    if s is None:
        return None
    # Primary format attempt
    try:
        return datetime.strptime(s, fmt).date()
    except Exception as e_first:
        # Optional fallbacks (keeps you productive while you standardize inputs)
        if try_formats:
            for f in try_formats:
                try:
                    return datetime.strptime(s, f).date()
                except Exception:
                    continue
        # If nothing worked, surface the original failure
        raise ValueError(f"not a date<{fmt}>: {v!r}")

def validate_value(field, raw_value, rules):
    errors = []
    value = raw_value

    # 1) Presence (required fields must not be missing/empty)
    if rules.get("required"):
        if is_missing(value):
            errors.append("required_missing")
            return None, errors

    # 2) Defaulting (only if missing/empty and default is provided)
    if is_missing(value) and "default" in rules:
        value = rules["default"]

    # 3) Type coercion (keep your existing block)
    expected_type = rules.get("type")
    if expected_type:
        try:
            if expected_type == "date":
                value = COERCERS["date"](
                    value,
                    fmt=rules.get("format"),
                    try_formats=rules.get("try_formats")
                )
            else:
                value = COERCERS[expected_type](value)
        except Exception:
            errors.append(f"type_error:{expected_type}")
            return value, errors

    # 3) Type coercion
    expected_type = rules.get("type")
    if expected_type:
        try:
            if expected_type == "date":
                value = COERCERS["date"](
                    value,
                    fmt=rules.get("format"),
                    try_formats=rules.get("try_formats")
                )
            else:
                value = COERCERS[expected_type](value)
        except Exception:
            errors.append(f"type_error:{expected_type}")
            return value, errors

    # 4) Pattern
    pattern = rules.get("pattern")
    if pattern and value is not None:
        import re
        if not re.match(pattern, str(value)):
            errors.append("pattern_mismatch")

       # 5) Allowed set (skip if None; compare post-coercion)
    allowed = rules.get("allowed")
    if allowed is not None and value is not None:
        if isinstance(value, str):
            candidate = value.strip()
            allowed_norm = [str(a).strip() for a in allowed]
            if candidate not in allowed_norm:
                errors.append("not_in_allowed_set")
        else:
            if value not in allowed:
                errors.append("not_in_allowed_set")

    # 6) Numeric constraints
    if isinstance(value, (int, float)):
        if "min" in rules and value < rules["min"]:
            errors.append("below_min")
        if "max" in rules and value > rules["max"]:
            errors.append("above_max")

    return value, errors
# --- Missing-value detection helper (uses same normalization rules as coercers) ---
def is_missing(v) -> bool:
    """
    Return True if value should be considered 'missing/empty' BEFORE defaults & type checks.
    Mirrors _normalize_raw rules so presence logic matches coercion behavior.
    """
    # Reuse the private normalizer if present
    try:
        s = _normalize_raw(v)  # from coercion section
    except NameError:
        # fallback: minimal behavior if _normalize_raw doesn't exist
        s = None if (v is None or str(v).strip() == "") else str(v).strip()
    return s is None

def enforce_nullable(field, value, rules, errors):
    """
    If field is optional but ends up None and nullable is False -> emit error.
    Default behavior: nullable=True (no error).
    """
    if value is None and not rules.get("required"):
        if rules.get("nullable") is False:
            errors.append("null_not_allowed")
    return value


COERCERS = {
    "str":   to_str,
    "int":   to_int,
    "float": to_float,
    "bool":  to_bool,
    # Pass schema's "format" and optional "try_formats" via the validator wrapper:
    "date":  lambda v, fmt=None, try_formats=None: to_date(v, fmt or "%Y-%m-%d", try_formats),
}
if __name__ == "__main__":
    import argparse
    import csv
    import json
    from pathlib import Path
    from src.io.csv_io import load_csv

    parser = argparse.ArgumentParser(description="Validate CSV rows against schema rules.")
    parser.add_argument("--in_csv", required=True, help="Input CSV file path")
    parser.add_argument("--schema", required=True, help="Schema JSON file path")
    parser.add_argument("--out", required=True, help="Output folder for reports")
    parser.add_argument("--fail_on_errors", action="store_true", help="Exit code 1 if any errors found")
    args = parser.parse_args()

    in_path = Path(args.in_csv)
    schema_path = Path(args.schema)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load schema and data
    schema = json.load(open(schema_path, encoding="utf-8"))["fields"]
    rows = load_csv(in_path)

    validation_errors = []
    valid_count = 0
    invalid_count = 0

    # Row-level validation
    for i, row in enumerate(rows, start=2):  # start=2 accounts for header line
        row_errors = []
        validated_row = {}
        for field, rules in schema.items():
            raw_value = row.get(field)
            value, errors = validate_value(field, raw_value, rules)
            validated_row[field] = value
            for err in errors:
                validation_errors.append({
                    "row": i,
                    "field": field,
                    "value": raw_value,
                    "error": err
                })
                row_errors.append(err)
        if row_errors:
            invalid_count += 1
        else:
            valid_count += 1

    # ---- Write reports ----
    error_csv = out_dir / "validation_errors.csv"
    summary_json = out_dir / "summary.json"

    # 1. Write CSV of errors
    with open(error_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["row", "field", "value", "error"])
        writer.writeheader()
        writer.writerows(validation_errors)

    # 2. Write summary JSON
    summary = {
        "total_rows": len(rows),
        "invalid_row_count": invalid_count,
        "valid_row_count": valid_count,
        "errors_total": len(validation_errors),
        "errors_by_field": {},
    }
    for e in validation_errors:
        summary["errors_by_field"].setdefault(e["field"], 0)
        summary["errors_by_field"][e["field"]] += 1

    with open(summary_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"✅ Validation complete. Errors: {len(validation_errors)}")
    print(f"📄 Error report: {error_csv}")
    print(f"📊 Summary:     {summary_json}")

    # Optional CI exit code
    if args.fail_on_errors and len(validation_errors) > 0:
        import sys
        sys.exit(1)
