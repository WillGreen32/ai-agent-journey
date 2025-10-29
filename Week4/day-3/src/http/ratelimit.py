from __future__ import annotations
import time
from typing import Any, Optional
from email.utils import parsedate_to_datetime

def _parse_retry_after(headers: dict, now_epoch: Optional[float] = None) -> int:
    """
    Parse Retry-After as either seconds or HTTP-date. Fallback to
    X-RateLimit-Reset (epoch seconds). Returns integer seconds >= 1.
    """
    now_epoch = now_epoch or time.time()
    raw = headers.get("Retry-After")

    # 1) Numeric seconds
    if raw is not None:
        try:
            secs = int(float(raw))
            return max(1, secs)
        except (ValueError, TypeError):
            # 2) HTTP-date form
            try:
                dt = parsedate_to_datetime(raw)
                wait = int(round(dt.timestamp() - now_epoch))
                return max(1, wait)
            except Exception:
                pass

    # 3) Fallback: X-RateLimit-Reset epoch
    reset_raw = headers.get("X-RateLimit-Reset") or headers.get("x-ratelimit-reset")
    if reset_raw is not None:
        try:
            reset_epoch = int(float(reset_raw))
            wait = int(round(reset_epoch - now_epoch))
            return max(1, wait)
        except (ValueError, TypeError):
            pass

    return 1

def handle_rate_limit(
    response: Any,
    *,
    min_sleep: int = 1,
    max_sleep: int = 300,
    logger: Optional[callable] = None,
    sleep_fn: callable = time.sleep,
) -> bool:
    """
    If response is 429, compute wait from Retry-After (or fallback), clamp
    to [min_sleep, max_sleep], sleep, and return True to signal 'retry'.
    """
    if response is None:
        return False

    status = getattr(response, "status_code", None)
    if status == 429:
        hdrs = getattr(response, "headers", {}) or {}
        secs = _parse_retry_after(hdrs)
        secs = max(min_sleep, min(int(secs), max_sleep))
        if logger:
            logger(f"[ratelimit] 429 received. Sleeping {secs}s.")
        else:
            print(f"[ratelimit] 429 received. Sleeping {secs}s.")
        sleep_fn(secs)
        return True

    return False
