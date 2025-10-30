# src/openapi/spec_utils.py
"""
Small helpers to:
- Load an OpenAPI (YAML/JSON) spec from URL or path
- List paths by filter
- Extract a response schema for a given operation (path+method+status+mime)
- Resolve $ref pointers (#/components/...)
"""

from __future__ import annotations
from typing import Any, Dict, Iterable, Optional
import json
import requests

try:
    import yaml  # requires pyyaml
except Exception as e:
    raise RuntimeError("pyyaml is required: pip install pyyaml") from e


# ---------- Loaders ----------

def load_openapi_from_url(url: str, *, timeout: float = 20.0) -> Dict[str, Any]:
    """Fetch and parse OpenAPI YAML/JSON from a URL."""
    headers = {"User-Agent": "Day4-Client/1.0 (OpenAPI Loader)"}
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    text = r.text
    # Try JSON first (some specs are JSON)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return yaml.safe_load(text)


# ---------- Path exploration ----------

def iter_paths(spec: Dict[str, Any], contains: Optional[str] = None) -> Iterable[str]:
    """Yield path strings; filter by substring if provided."""
    paths = spec.get("paths", {}) or {}
    for p in paths.keys():
        if contains is None or contains in p:
            yield p


# ---------- $ref resolving ----------

def _resolve_pointer(doc: Dict[str, Any], pointer: str) -> Any:
    """
    Resolve a JSON Pointer like '#/components/schemas/Whatever'.
    Only supports in-document refs (starting with '#/').
    """
    if not pointer.startswith("#/"):
        raise ValueError(f"External refs not supported in this helper: {pointer}")
    parts = pointer[2:].split("/")
    cur: Any = doc
    for part in parts:
        # Unescape JSON Pointer tokens
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            raise KeyError(f"Pointer segment not found: {part} in {pointer}")
    return cur

def deref(schema: Any, spec: Dict[str, Any]) -> Any:
    """
    Recursively resolve $ref within a schema node (returns a deep-dereferenced copy).
    Only handles in-document $refs. Keeps other keys intact.
    """
    if isinstance(schema, dict):
        if "$ref" in schema:
            target = _resolve_pointer(spec, schema["$ref"])
            # Merge: referenced content can be extended by sibling keys per OAS
            merged = {k: v for k, v in schema.items() if k != "$ref"}
            resolved = deref(target, spec)
            if merged:
                # 'allOf' semantics: override/extend resolved with siblings
                if isinstance(resolved, dict):
                    out = dict(resolved)
                    out.update(merged)
                    return out
            return resolved
        # Recurse into dict
        return {k: deref(v, spec) for k, v in schema.items()}
    if isinstance(schema, list):
        return [deref(v, spec) for v in schema]
    return schema


# ---------- Operation schema extraction ----------

def get_response_schema(
    spec: Dict[str, Any],
    path: str,
    method: str = "get",
    status: str = "200",
    mime: str = "application/json",
    dereference: bool = True,
) -> Dict[str, Any]:
    """
    Return the JSON Schema for a given operation response.
    """
    paths = spec.get("paths", {})
    op = paths.get(path, {})
    op_obj = op.get(method.lower())
    if not op_obj:
        raise KeyError(f"No operation {method} defined for path {path}")

    responses = op_obj.get("responses", {})
    r = responses.get(status) or responses.get(int(status))  # tolerate int keys
    if not r:
        raise KeyError(f"No response {status} for {method} {path}")

    content = r.get("content", {})
    c = content.get(mime)
    if not c:
        raise KeyError(f"No content {mime} on {status} for {method} {path}")

    schema = c.get("schema")
    if not schema:
        raise KeyError("No schema found in content")

    return deref(schema, spec) if dereference else schema
