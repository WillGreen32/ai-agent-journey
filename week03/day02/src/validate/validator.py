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
    
# --- Error reporting writers --------------------------------------------------
import csv, json, os
from collections import Counter

def write_error_report(errors, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "validation_errors.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["row", "field", "value", "error"])
        writer.writeheader()
        writer.writerows(errors)
    return path

def build_summary(validated_rows, errors):
    total = len(validated_rows)
    invalid_rows = {e["row"] for e in errors}
    by_field = Counter(e["field"] for e in errors)
    by_error = Counter(e["error"] for e in errors)

    # Top 10 sample errors for quick inspection
    sample = errors[:10]

    return {
        "total_rows": total,
        "invalid_row_count": len(invalid_rows),
        "valid_row_count": total - len(invalid_rows),
        "errors_total": len(errors),
        "errors_by_field": dict(by_field),
        "errors_by_code": dict(by_error),
        "sample_errors": sample
    }

def write_summary(summary, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "summary.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    return path
    

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

# --- Regex compile cache + helper --------------------------------------------
_REGEX_CACHE = {}

_FLAG_MAP = {
    "IGNORECASE": re.IGNORECASE,
    "MULTILINE": re.MULTILINE,
    "DOTALL": re.DOTALL,
    "ASCII": re.ASCII,
    "UNICODE": re.UNICODE,  # default in Py3, but allow explicit
}

def _compile_pattern(pattern: str, flags: list | None):
    """Compile and cache regex with optional flags from schema."""
    key = (pattern, tuple(flags or []))
    if key in _REGEX_CACHE:
        return _REGEX_CACHE[key]
    fmask = 0
    if flags:
        for name in flags:
            fmask |= _FLAG_MAP.get(name.upper(), 0)
    rex = re.compile(pattern, fmask)
    _REGEX_CACHE[key] = rex
    return rex

def matches_pattern(value, pattern, flags=None) -> bool:
    """
    Return True if value fully matches regex pattern. 
    Empty/None values are treated as 'not applicable' and pass.
    """
    if value is None:
        return True
    s = str(value)
    if s.strip() == "":
        return True
    try:
        rex = _compile_pattern(pattern, flags)
        return bool(rex.fullmatch(s))
    except re.error:
        # If the pattern itself is invalid, treat as mismatch (or you could log a schema error)
        return False


    # --- Pattern validation (e.g., email) ---
    pattern = rules.get("pattern")
    if pattern and isinstance(value, str):
        flags = rules.get("pattern_flags")  # optional: ["IGNORECASE", "MULTILINE", ...]
        if not matches_pattern(value, pattern, flags):
            errors.append("pattern_mismatch")


def validate_row(row_idx: int, row: dict, schema: dict):
    """
    Validate one CSV row (dict) against schema['fields'].
    Returns: (validated_row: dict, row_errors: list[dict])
    """
    row_errors = []
    validated = {}

    # schema is expected to be the full object with "fields": {...}
    fields = schema["fields"] if "fields" in schema else schema

    for field, rules in fields.items():
        raw = row.get(field)
        value, errs = validate_value(field, raw, rules)
        validated[field] = value

        if errs:
            for e in errs:
                row_errors.append({
                    "row": row_idx,     # CSV row number with header offset applied by caller
                    "field": field,
                    "value": raw,
                    "error": e
                })

    return validated, row_errors


def validate_dataset(rows: list[dict], schema: dict, header_offset: int = 1):
    """
    Validate all rows in a dataset.
    header_offset=1 means the header occupies row 1; first data row is 2.
    Returns: (validated_rows, all_errors)
    """
    all_errors = []
    validated_rows = []

    for i, row in enumerate(rows, start=1 + header_offset):
        vrow, rerrs = validate_row(i, row, schema)
        validated_rows.append(vrow)
        all_errors.extend(rerrs)

    return validated_rows, all_errors

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

