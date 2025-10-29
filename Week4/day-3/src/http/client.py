from __future__ import annotations
import requests
from typing import Any, Dict, Optional, Callable

from .retry import retry_with_backoff, exponential_backoff_retry, RETRYABLE_STATUSES
from .ratelimit import handle_rate_limit
from .idempotency import (
    generate_idempotency_key,
    canonical_body_hash,
    cache_get,
    cache_put,
)

class HttpClient:
    """
    A minimal, robust HTTP client:
      • GET/HEAD/OPTIONS: safe retries with backoff+jitter
      • POST/PUT: idempotency keys + local response cache
      • All: respects 429 Retry-After via handle_rate_limit()
    """

    def __init__(self, base_url: str, session: Optional[requests.Session] = None, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.timeout = timeout

    # ---------- Helpers ----------

    def _full_url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _retryable_result(self, resp: requests.Response) -> bool:
        return getattr(resp, "status_code", None) in RETRYABLE_STATUSES

    def _retryable_exc(self, e: BaseException) -> bool:
        return isinstance(
            e,
            (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError,
                requests.exceptions.RetryError,
            ),
        )

    # ---------- Safe methods (GET/HEAD/OPTIONS) ----------

    def _request_with_rate_limit(self, fn: Callable[[], requests.Response]) -> requests.Response:
        """Call `fn` respecting 429 and retrying transient failures."""
        def do_request():
            resp = fn()
            # First, respect server pacing
            if handle_rate_limit(resp):
                # Signal to retry engine that we paused and should try again
                raise requests.exceptions.RetryError("429 handled; retrying")
            return resp

        resp = retry_with_backoff(
            do_request,
            is_retryable_result=self._retryable_result,
            is_retryable_exc=self._retryable_exc,
            jitter="decorrelated",
            max_retries=5,
            base_delay=0.5,
            max_delay=8.0,
        )
        return resp

    def get(self, path: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        url = self._full_url(path)
        headers = headers or {}

        resp = self._request_with_rate_limit(lambda: self.session.get(url, params=params, headers=headers, timeout=self.timeout))
        resp.raise_for_status()
        return resp

    # ---------- Idempotent writes (POST/PUT) ----------

    def _write_idempotent(
        self,
        method: str,
        path: str,
        json_body: Dict[str, Any],
        *,
        idempotency_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        max_retries: int = 5,
    ) -> Dict[str, Any]:
        url = self._full_url(path)
        headers = dict(headers or {})
        key = idempotency_key or generate_idempotency_key()
        body_hash = canonical_body_hash(json_body)

        # Local cache fast-path:
        cached = cache_get(method, url, key)
        if cached:
            if cached["body_hash"] != body_hash:
                raise ValueError("Idempotency-Key reuse with different payload detected.")
            return cached["response"]

        def do_request():
            final_headers = {"Idempotency-Key": key, "Content-Type": "application/json", **headers}
            resp = self.session.request(method, url, headers=final_headers, json=json_body, timeout=self.timeout)

            # Respect server pacing first
            if handle_rate_limit(resp):
                raise requests.exceptions.RetryError("429 handled; retrying")

            # Transient statuses → retry
            if resp.status_code in RETRYABLE_STATUSES:
                raise requests.exceptions.RetryError(f"Transient {resp.status_code}")

            resp.raise_for_status()
            return resp

        # Use simple wrapper for clarity here; could also use retry_with_backoff like GET.
        response = exponential_backoff_retry(do_request, max_retries=max_retries, base_delay=0.5)
        data = response.json() if hasattr(response, "json") else {"status": response.status_code}

        # Persist success result for the (method|url|key)
        cache_put(method, url, key, body_hash, data)
        return data

    def post(self, path: str, json_body: Dict[str, Any], *, idempotency_key: Optional[str] = None, headers: Optional[Dict[str, str]] = None, max_retries: int = 5) -> Dict[str, Any]:
        return self._write_idempotent("POST", path, json_body, idempotency_key=idempotency_key, headers=headers, max_retries=max_retries)

    def put(self, path: str, json_body: Dict[str, Any], *, idempotency_key: Optional[str] = None, headers: Optional[Dict[str, str]] = None, max_retries: int = 5) -> Dict[str, Any]:
        return self._write_idempotent("PUT", path, json_body, idempotency_key=idempotency_key, headers=headers, max_retries=max_retries)
