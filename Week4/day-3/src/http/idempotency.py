from __future__ import annotations
import os, json, uuid, time, hashlib, tempfile
from typing import Any, Dict, Optional

# Local JSON file used as a lightweight idempotency store.
# In real systems you’d use Redis/DB; this is perfect for learning & demos.
CACHE_FILE = "idempotency_cache.json"
DEFAULT_TTL_SECONDS = 24 * 3600  # 24h

# ---------- Public API ----------

def generate_idempotency_key() -> str:
    """Return a new UUIDv4 string for POST/PUT idempotent operations."""
    return str(uuid.uuid4())

def canonical_body_hash(body: Any) -> str:
    """
    Stable SHA-256 hash of the request body.
    We JSON-encode with sorted keys so logically-equal payloads hash the same.
    """
    payload = json.dumps(body, sort_keys=True, separators=(",", ":")) if body is not None else ""
    return hashlib.sha256(payload.encode()).hexdigest()

def cache_put(
    method: str,
    url: str,
    key: str,
    body_hash: str,
    response_data: Dict[str, Any],
    ttl: int = DEFAULT_TTL_SECONDS,
) -> None:
    """
    Store the first successful response for (method|url|key).
    - body_hash is stored so callers can detect key reuse with different payloads.
    - ttl controls how long an entry remains valid.
    """
    cache = _load_cache()
    cache_key = _compose_cache_key(method, url, key)
    cache[cache_key] = {
        "body_hash": body_hash,
        "response": response_data,
        "stored_at": int(time.time()),
        "ttl": int(ttl),
    }
    _save_cache_atomic(cache)

def cache_get(method: str, url: str, key: str) -> Optional[Dict[str, Any]]:
    """
    Return cached entry dict {body_hash, response, stored_at, ttl} or None if
    not found/expired. Expired entries are cleaned up opportunistically.
    """
    cache = _load_cache()
    cache_key = _compose_cache_key(method, url, key)
    item = cache.get(cache_key)
    if not item:
        return None

    now = int(time.time())
    if now - item.get("stored_at", now) > item.get("ttl", DEFAULT_TTL_SECONDS):
        # Expired: remove and persist cleanup
        cache.pop(cache_key, None)
        _save_cache_atomic(cache)
        return None
    return item

def cache_cleanup() -> int:
    """Remove expired entries; return number of items removed."""
    cache = _load_cache()
    now = int(time.time())
    removed = 0
    for k, v in list(cache.items()):
        if now - v.get("stored_at", now) > v.get("ttl", DEFAULT_TTL_SECONDS):
            cache.pop(k, None)
            removed += 1
    if removed:
        _save_cache_atomic(cache)
    return removed

# ---------- Internals ----------

def _compose_cache_key(method: str, url: str, key: str) -> str:
    return f"{method.upper()}|{url}|{key}"

def _load_cache() -> Dict[str, Any]:
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Corrupt or unreadable: safest to reset.
        return {}

def _save_cache_atomic(cache: Dict[str, Any]) -> None:
    """
    Write cache to disk atomically to reduce risk of partial writes:
    write to a temp file, then replace.
    """
    dirpath = os.path.dirname(os.path.abspath(CACHE_FILE)) or "."
    fd, tmp_path = tempfile.mkstemp(prefix="idem_", suffix=".json", dir=dirpath)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp:
            json.dump(cache, tmp)
        os.replace(tmp_path, CACHE_FILE)
    finally:
        # If anything went wrong after mkstemp but before replace, clean up.
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
