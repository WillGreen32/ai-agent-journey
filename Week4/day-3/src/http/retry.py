from __future__ import annotations
import time, random
from typing import Callable, TypeVar, Optional, Any, Iterable, Tuple

T = TypeVar("T")

# Common transient HTTP status codes (useful if your request_func returns a response)
RETRYABLE_STATUSES = {408, 500, 502, 503, 504}

class RetryError(RuntimeError):
    """Raised when all retries are exhausted."""
    pass

# ---- Jitter calculators ------------------------------------------------------

def _jitter_full(delay: float) -> float:
    # Uniform(0, delay)
    return random.uniform(0.0, max(delay, 0.0))

def _jitter_equal(delay: float) -> float:
    # delay/2 + Uniform(0, delay/2)
    half = max(delay, 0.0) / 2.0
    return half + random.uniform(0.0, half)

def _jitter_decorrelated(prev: float, base: float, cap: float) -> float:
    # From AWS "Exponential Backoff And Jitter" blog: min(cap, random(base, prev*3))
    low = max(base, 0.0)
    high = max(prev * 3.0, low)
    return min(cap, random.uniform(low, high))

def _sleep_seconds(seconds: float) -> None:
    if seconds > 0:
        time.sleep(seconds)

# ---- Core configurable retry -------------------------------------------------

def retry_with_backoff(
    fn: Callable[[], T],
    *,
    max_retries: int = 5,
    base_delay: float = 0.5,
    max_delay: float = 30.0,
    jitter: str = "full",  # "full" | "equal" | "decorrelated" | "none"
    max_elapsed: Optional[float] = None,  # total wall-clock budget (seconds)
    is_retryable_exc: Optional[Callable[[BaseException], bool]] = None,
    is_retryable_result: Optional[Callable[[Any], bool]] = None,
    on_retry: Optional[Callable[[int, BaseException | None, float], None]] = None,
    logger: Optional[Callable[[str], None]] = None,
    sleep_fn: Callable[[float], None] = _sleep_seconds,
) -> T:
    """
    Execute `fn()` with exponential backoff and jitter until it succeeds
    or retry budget is exceeded.

    Parameters:
      - max_retries: number of retry *attempts* (not counting the initial try).
      - base_delay: initial backoff (seconds); grows exponentially.
      - max_delay: cap for any single sleep.
      - jitter: backoff randomization mode ("full" | "equal" | "decorrelated" | "none").
      - max_elapsed: optional total wall-clock time limit across all tries.
      - is_retryable_exc(e): return True to retry on the exception, else raise.
      - is_retryable_result(r): return True if the result should be retried (e.g., 5xx).
      - on_retry(attempt, last_exception, sleep_seconds): hook for logging/metrics.
      - logger(msg): simple logger hook; if provided, used for debug strings.
      - sleep_fn(seconds): injectable sleep function for tests.

    Returns:
      The successful result of `fn()`.

    Raises:
      RetryError if retries are exhausted or time budget exceeded,
      or the original exception for non-retryable failures.
    """
    start = time.monotonic()
    attempt = 0
    prev_delay = base_delay

    def _log(msg: str) -> None:
        if logger:
            logger(msg)

    while True:
        try:
            result = fn()
            # Decide if the *result* should be retried (e.g., a response with 5xx)
            if is_retryable_result and is_retryable_result(result):
                raise _ResultRetrySignal(result)  # handled below as retryable
            return result

        except _ResultRetrySignal as rrs:
            # Treat as a retryable condition using the same path as exceptions.
            last_exc: Optional[BaseException] = None

        except BaseException as e:
            # If not retryable, re-raise immediately.
            if is_retryable_exc and not is_retryable_exc(e):
                raise
            last_exc = e

        # If we get here, we must retry (either result said so, or exception is retryable)
        if attempt >= max_retries:
            raise RetryError(f"All retries exhausted after {attempt} retries.") from (last_exc if 'last_exc' in locals() else None)

        # Check elapsed budget
        if max_elapsed is not None:
            elapsed = time.monotonic() - start
            if elapsed >= max_elapsed:
                raise RetryError(f"Retry time budget exceeded (elapsed {elapsed:.2f}s).") from (last_exc if 'last_exc' in locals() else None)

        # Compute base exponential delay
        exp_delay = min(base_delay * (2 ** attempt), max_delay)

        # Apply jitter
        if jitter == "none":
            sleep_for = exp_delay
        elif jitter == "full":
            sleep_for = _jitter_full(exp_delay)
        elif jitter == "equal":
            sleep_for = _jitter_equal(exp_delay)
        elif jitter == "decorrelated":
            # uses previous delay to avoid synchronization and big leaps
            sleep_for = _jitter_decorrelated(prev_delay, base_delay, max_delay)
        else:
            sleep_for = _jitter_full(exp_delay)  # default safety

        # If max_elapsed is set, ensure we don't overshoot the budget too much
        if max_elapsed is not None:
            elapsed = time.monotonic() - start
            remaining = max_elapsed - elapsed
            if remaining <= 0:
                raise RetryError(f"Retry time budget exceeded (elapsed {elapsed:.2f}s).") from (last_exc if 'last_exc' in locals() else None)
            # don't sleep longer than remaining budget
            sleep_for = max(0.0, min(sleep_for, remaining))

        if on_retry:
            on_retry(attempt + 1, (last_exc if 'last_exc' in locals() else None), sleep_for)

        _log(f"[retry] attempt={attempt+1} sleeping={sleep_for:.3f}s jitter={jitter}")
        sleep_fn(sleep_for)
        prev_delay = sleep_for if jitter == "decorrelated" else exp_delay
        attempt += 1


class _ResultRetrySignal(Exception):
    """Internal: used to signal that a *result* should be retried."""
    def __init__(self, result: Any):
        self.result = result


# ---- Backwards-compatible wrapper -------------------------------------------

def exponential_backoff_retry(
    request_func: Callable[[], T],
    max_retries: int = 5,
    base_delay: float = 1.0,
    jitter_range: float = 0.5,  # kept for backward-compat with earlier tests
) -> T:
    """
    Legacy helper kept for compatibility with earlier lessons.

    Retries when `request_func` raises exceptions (any kind), using
    exponential backoff + full jitter. Raises RetryError after exhausting retries.

    Note: `jitter_range` is accepted for backward-compat but not used,
    because jitter is handled by the internal strategy.
    """
    def _logger(msg: str) -> None:
        print(msg)

    return retry_with_backoff(
        request_func,
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=30.0,
        jitter="full",
        is_retryable_exc=lambda e: True,
        logger=_logger,
    )
