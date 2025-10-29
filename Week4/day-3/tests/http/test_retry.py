from src.http.retry import exponential_backoff_retry

def test_retry_eventually_succeeds():
    calls = {"n": 0}
    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("transient")
        return "ok"
    result = exponential_backoff_retry(flaky, max_retries=5, base_delay=0.001, jitter_range=0)
    assert result == "ok"
