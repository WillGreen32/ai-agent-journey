import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src.http.retry import exponential_backoff_retry
import requests

def call_api():
    # httpbin can return 503 once then 200: use /status/503 to force failure first,
    # or /status/503,200 to sometimes flip between 503 and 200.
    r = requests.get("https://httpbin.org/status/503,200", timeout=5)
    r.raise_for_status()
    return r.status_code

if __name__ == "__main__":
    result = exponential_backoff_retry(call_api, max_retries=5, base_delay=0.5)
    print("Final result:", result)

