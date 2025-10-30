import os, json, hashlib
from typing import Any, Optional

CACHE_DIR = ".cache"

def _key_path(key: str) -> str:
    os.makedirs(CACHE_DIR, exist_ok=True)
    h = hashlib.sha1(key.encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, f"{h}.json")

class SimpleCache:
    """Tiny file-based cache of {'etag': str, 'data': Any} per key."""
    def read(self, key: str) -> Optional[dict]:
        path = _key_path(key)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def write(self, key: str, etag: str, data: Any) -> None:
        path = _key_path(key)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"etag": etag, "data": data}, f)
