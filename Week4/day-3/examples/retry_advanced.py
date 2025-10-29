import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src.http.retry import retry_with_backoff, RETRYABLE_STATUSES
import requests

def call_api():
    # This endpoint returns 503 or 200 randomly
    return requests.get("https://httpbin.org/status/503,200", timeout=5)

def is_retryable_result(resp):
    return getattr(resp, "status_code", None) in RETRYABLE_STATUSES

def is_retryable_exc(e):
    return isinstance(e, (requests.exceptions.Timeout,
                          requests.exceptions.ConnectionError,
                          requests.exceptions.HTTPError))

def on_retry(attempt, exc, sleep_s):
    print(f"[on_retry] attempt={attempt} sleep={sleep_s:.2f}s exc={type(exc).__name__ if exc else None}")

if __name__ == "__main__":
    resp = retry_with_backoff(
        call_api,
        max_retries=5,
        base_delay=0.5,
        max_delay=8.0,
        jitter="decorrelated",
        is_retryable_result=is_retryable_result,
        is_retryable_exc=is_retryable_exc,
        on_retry=on_retry,
    )
    print("Final HTTP status:", resp.status_code)

