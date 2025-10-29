from src.http.idempotency import generate_idempotency_key, canonical_body_hash, cache_put, cache_get

def test_idempotency_cache_roundtrip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    key = generate_idempotency_key()
    body_hash = canonical_body_hash({"a": 1, "b": 2})
    url = "https://api.example.com/orders"
    cache_put("POST", url, key, body_hash, {"ok": True})
    item = cache_get("POST", url, key)
    assert item is not None
    assert item["body_hash"] == body_hash
    assert item["response"]["ok"] is True
