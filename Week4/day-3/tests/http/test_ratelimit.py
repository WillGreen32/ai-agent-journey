from types import SimpleNamespace
from src.http.ratelimit import handle_rate_limit, _parse_retry_after
import time

def _nosleep(_s):  # test stub to avoid real sleeping
    pass

def test_parse_retry_after_seconds():
    now = time.time()
    secs = _parse_retry_after({"Retry-After": "5"}, now_epoch=now)
    assert secs == 5

def test_parse_retry_after_http_date():
    # 3 seconds in the future
    target = time.time() + 3
    http_date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(target))
    secs = _parse_retry_after({"Retry-After": http_date}, now_epoch=target - 0.2)
    assert 1 <= secs <= 3  # allow rounding wiggle

def test_parse_fallback_x_ratelimit_reset():
    target = int(time.time()) + 7
    secs = _parse_retry_after({"X-RateLimit-Reset": str(target)}, now_epoch=target - 1)
    assert secs == 1  # 1 second remaining (clamped min=1)

def test_handle_rate_limit_429_seconds(monkeypatch, capsys):
    resp = SimpleNamespace(status_code=429, headers={"Retry-After": "0"})
    assert handle_rate_limit(resp, sleep_fn=_nosleep) is True
    # printed message visible
    out = capsys.readouterr().out
    assert "429" in out

def test_handle_rate_limit_not_triggered():
    resp = SimpleNamespace(status_code=200, headers={})
    assert handle_rate_limit(resp, sleep_fn=_nosleep) is False
