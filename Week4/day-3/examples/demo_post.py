import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
"""
A tiny demo that shows how a single business operation can be retried safely.
This uses httpbin.org/post for a harmless echo (no double-charge risk).
"""
import os
import requests
from src.http.client import HttpClient
from src.http.idempotency import generate_idempotency_key

def main():
    base = os.environ.get("API_BASE_URL", "https://httpbin.org")
    client = HttpClient(base)

    payload = {"sku": "ABC-123", "qty": 1}
    key = generate_idempotency_key()

    # Try twice with the same key (simulating a network hiccup + retry)
    first = client.post_idempotent("/post", payload, idempotency_key=key, max_retries=2)
    second = client.post_idempotent("/post", payload, idempotency_key=key, max_retries=2)

    print("Equal responses? ->", first == second)
    print("Sample response keys:", list(first.keys())[:5])

if __name__ == "__main__":
    main()

