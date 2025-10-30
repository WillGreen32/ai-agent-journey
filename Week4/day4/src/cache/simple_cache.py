# src/cache/simple_cache.py
import os, json, time, hashlib, requests
from typing import Any, Optional

CACHE_DIR = "cache"
DEFAULT_TTL = 86400  # 1 day (fallback if no ETag supported)

def _cache_path(url: str) -> str:
    key = hashlib.md5(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{key}.json")

def get_with_cache(url: str, ttl: int = DEFAULT_TTL) -> Any:
    """Fetch a URL with ETag caching and TTL fallback."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = _cache_path(url)

    etag = None
    cached_data: Optional[dict] = None

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            cached_data = json.load(f)
        etag = cached_data.get("etag")
        # TTL fallback if API doesn't support ETag
        if not cached_data.get("etag") and (time.time() - cached_data.get("timestamp", 0)) < ttl:
            print("Cache hit! (TTL)")
            return cached_data["data"]

    headers = {"If-None-Match": etag} if etag else {}
    r = requests.get(url, headers=headers)
    r.raise_for_status()

    # Case 1: Unchanged
    if r.status_code == 304 and cached_data:
        print("Cache hit! (ETag)")
        return cached_data["data"]

    # Case 2: New or changed
    data = r.json()
    new_record = {
        "etag": r.headers.get("ETag"),
        "timestamp": time.time(),
        "data": data,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(new_record, f)

    print("Cache miss → saved new data")
    return data


if __name__ == "__main__":
    url = "https://api.github.com/repos/openai/openai-python"  # ✅ real repo
    print("First call → fetch from network")
    data1 = get_with_cache(url)
    print("Second call → should be a cache hit")
    data2 = get_with_cache(url)
    print("Same data:", data1 == data2)

