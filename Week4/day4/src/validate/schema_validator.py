# src/validate/schema_validator.py
"""
Lightweight JSON Schema validation utilities.

Features:
- clear error messages with JSON path (e.g., $.owner.login)
- optional strict mode
- compiled validators with LRU cache for speed
- validate single objects or lists of objects
- simple loader for JSON/YAML schemas
"""

from __future__ import annotations
from typing import Any, Dict, Iterable, Optional, Tuple, Union
from functools import lru_cache
import json
import os

from jsonschema import Draft202012Validator, ValidationError, FormatChecker

try:
    import yaml  # optional (installed earlier via pyyaml)
    _HAS_YAML = True
except Exception:
    _HAS_YAML = False

JsonObj = Union[Dict[str, Any], list, str, int, float, bool, None]

# ---------- helpers -----------------------------------------------------------

def _json_path(error: ValidationError) -> str:
    """Return a human-friendly JSONPath-like pointer to the failing location."""
    # error.path is a deque of keys/indices; build "$.a.b[3]" style
    parts = ["$"]
    for p in error.path:
        if isinstance(p, int):
            parts.append(f"[{p}]")
        else:
            parts.append(f".{p}")
    return "".join(parts)

def _format_error(e: ValidationError, label: Optional[str]) -> str:
    where = f" in '{label}'" if label else ""
    loc = _json_path(e)
    return f"Schema validation failed{where} at {loc}: {e.message}"

def load_schema(schema: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Load a schema from a dict or a JSON/YAML file path.
    """
    if isinstance(schema, dict):
        return schema
    if not isinstance(schema, str):
        raise TypeError("schema must be dict or file path str")

    if not os.path.exists(schema):
        raise FileNotFoundError(f"Schema file not found: {schema}")

    with open(schema, "r", encoding="utf-8") as f:
        text = f.read()

    # Try JSON, then YAML
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        if not _HAS_YAML:
            raise
        return yaml.safe_load(text)

# ---------- validator core ----------------------------------------------------

@lru_cache(maxsize=64)
def _compile_validator_cached(schema_text: str, strict: bool) -> Draft202012Validator:
    """
    Compile and cache a jsonschema validator.
    Note: We cache by schema_text string to allow hashing.
    """
    schema = json.loads(schema_text)
    # Draft2020-12 + optional strict rules (e.g., forbid additional properties)
    format_checker = FormatChecker()
    return Draft202012Validator(schema, format_checker=format_checker)

def compile_validator(schema: Dict[str, Any], *, strict: bool = False) -> Draft202012Validator:
    """
    Compile a schema into a validator object (fast for repeated calls).
    """
    # In strict mode you can pre-enforce patterns like "additionalProperties": False
    # at your schema authoring time. We just pass the flag through for future use.
    schema_text = json.dumps(schema, sort_keys=True)
    return _compile_validator_cached(schema_text, strict)

def validate_response(
    data: JsonObj,
    schema: Dict[str, Any],
    *,
    label: Optional[str] = None,
    strict: bool = False,
    raise_on_error: bool = True,
    verbose: bool = True,
) -> bool:
    """
    Validate `data` against `schema`.
    Returns True on success.
    On failure:
      - if raise_on_error=True, raises ValidationError with a readable message
      - else returns False
    """
    validator = compile_validator(schema, strict=strict)
    try:
        validator.validate(data)
        if verbose:
            print("✅ Schema valid" + (f" ({label})" if label else ""))
        return True
    except ValidationError as e:
        msg = _format_error(e, label)
        if raise_on_error:
            # re-raise with improved message
            raise ValidationError(msg) from e
        else:
            if verbose:
                print("❌", msg)
            return False

def validate_many(
    items: Iterable[JsonObj],
    item_schema: Dict[str, Any],
    *,
    label: Optional[str] = None,
    strict: bool = False,
    raise_on_error: bool = True,
    verbose: bool = True,
) -> Tuple[int, int]:
    """
    Validate a sequence of objects against `item_schema`.
    Returns (ok_count, fail_count)
    """
    ok = fail = 0
    validator = compile_validator(item_schema, strict=strict)
    for idx, item in enumerate(items):
        try:
            validator.validate(item)
            ok += 1
        except ValidationError as e:
            fail += 1
            msg = _format_error(e, f"{label}[{idx}]" if label else f"item[{idx}]")
            if raise_on_error:
                raise ValidationError(msg) from e
            elif verbose:
                print("❌", msg)
    if verbose:
        print(f"Validation summary: {ok} ok, {fail} failed")
    return ok, fail


from src.validate.schema_validator import validate_response

schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "private": {"type": "boolean"},
        "owner": {
            "type": "object",
            "properties": {
                "login": {"type": "string"},
                "id": {"type": "integer"}
            },
            "required": ["login", "id"]
        }
    },
    "required": ["id", "name", "owner"]
}

# Suppose `data` came from your cache or requests.get(...).json()
# validate_response(data, schema, label="GitHub repo")

from src.validate.schema_validator import validate_many

item_schema = {
  "type": "object",
  "properties": {"id": {"type": "integer"}, "name": {"type":"string"}},
  "required": ["id", "name"]
}

# validate_many(list_of_repos, item_schema, label="repos")

from src.validate.schema_validator import load_schema, validate_response
my_schema = load_schema("schemas/repo_schema.json")  # or .yaml
# validate_response(data, my_schema, label="GitHub repo")

from src.validate.schema_validator import validate_response

def page_validator(page: dict) -> None:
    # Example: ensure page is a list of repos
    item_schema = {
      "type":"object",
      "properties":{"id":{"type":"integer"}, "name":{"type":"string"}},
      "required":["id","name"]
    }
    if isinstance(page, list):
        # Validate a sample or all (you choose)
        for i, item in enumerate(page[:5]):
            validate_response(item, item_schema, label=f"repo[{i}]")
    else:
        # If wrapped in {"items": [...]}
        validate_response(page, {"type":"object", "properties":{"items":{"type":"array"}}, "required":["items"]}, label="page")

# pass validator=page_validator into paginate_cursor / paginate_page_limit
