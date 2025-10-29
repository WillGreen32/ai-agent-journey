# src/auth/strategies.py
from __future__ import annotations
import os, hmac, hashlib, time, secrets
from typing import Dict, Optional
from dotenv import load_dotenv

# Load .env once at import time for simple scripts.
# In bigger apps, you may centralize load_dotenv() in the entrypoint.
load_dotenv()

class AuthConfigError(ValueError):
    """Raised when a required secret/env var is missing."""

def _require_env(name: str) -> str:
    """Fetch a required env var or raise a helpful error."""
    val = os.getenv(name)
    if not val:
        raise AuthConfigError(f"Missing required environment variable: {name}")
    return val

def _attach(headers: Optional[Dict[str, str]]) -> Dict[str, str]:
    """Guarantee a dict for header mutation."""
    return {} if headers is None else headers

class ApiKeyAuth:
    """
    Header-based API key auth.
    Usage:
        auth = ApiKeyAuth()  # expects API_KEY in env
        headers = auth.attach({})
    """
    def __init__(self, key_env: str = "API_KEY", key_name: str = "X-API-Key"):
        self.api_key = _require_env(key_env)
        self.key_name = key_name

    def attach(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = _attach(headers)
        headers[self.key_name] = self.api_key
        return headers

class BearerAuth:
    """
    Static bearer token auth (useful for quick tests or fixed service tokens).
    """
    def __init__(self, token_env: str = "BEARER_TOKEN"):
        self.token = _require_env(token_env)

    def attach(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = _attach(headers)
        headers["Authorization"] = f"Bearer {self.token}"
        return headers

class HmacAuth:
    """
    HMAC-SHA256 signing helper.
    - sign(message) -> hex digest
    - signed_headers(...) -> returns headers you can send with the request
    """
    def __init__(self, secret_env: str = "HMAC_SECRET"):
        self.secret = _require_env(secret_env).encode()

    def sign(self, message: str) -> str:
        """Return hex SHA-256 HMAC signature for the message."""
        return hmac.new(self.secret, message.encode(), hashlib.sha256).hexdigest()

    def signed_headers(
        self,
        message: str,
        key_id_env: str = "HMAC_KEY_ID",
        include_timestamp: bool = True,
        include_nonce: bool = True,
    ) -> Dict[str, str]:
        """
        Produces common HMAC-style headers:
          - X-Key-Id (public identifier for the secret)
          - X-Signature (hex digest)
          - X-Timestamp (unix seconds)  [prevents replay]
          - X-Nonce (random)            [prevents replay]
        """
        headers: Dict[str, str] = {}
        key_id = os.getenv(key_id_env, "default")
        ts = str(int(time.time()))
        nonce = secrets.token_hex(8)

        # Build the signed payload deterministically
        payload = message
        if include_timestamp:
            payload += f"|{ts}"
            headers["X-Timestamp"] = ts
        if include_nonce:
            payload += f"|{nonce}"
            headers["X-Nonce"] = nonce

        headers["X-Key-Id"] = key_id
        headers["X-Signature"] = self.sign(payload)
        return headers


import requests
from typing import Tuple

class OAuthError(RuntimeError):
    """Raised for OAuth token fetch/parse failures."""

class OAuthClientCredentials:
    """
    OAuth 2.0 Client Credentials flow with caching + pre-expiry refresh.
    Env vars:
      - OAUTH_TOKEN_URL (e.g., https://auth.example.com/oauth/token)
      - CLIENT_ID
      - CLIENT_SECRET
      - OAUTH_SCOPE (optional, space-separated)
    """
    def __init__(
        self,
        token_url_env: str = "OAUTH_TOKEN_URL",
        client_id_env: str = "CLIENT_ID",
        client_secret_env: str = "CLIENT_SECRET",
        scope_env: str = "OAUTH_SCOPE",
        timeout: float = 10.0,
        refresh_skew: int = 60,   # refresh 60s before expiry
        max_retries: int = 2,     # total attempts = max_retries + 1
    ):
        self.token_url = _require_env(token_url_env)
        self.client_id = _require_env(client_id_env)
        self.client_secret = _require_env(client_secret_env)
        self.scope = os.getenv(scope_env)  # optional
        self.timeout = timeout
        self.refresh_skew = refresh_skew
        self.max_retries = max_retries

        self._token: Optional[str] = None
        self._expires_at: float = 0.0

    def _needs_refresh(self) -> bool:
        # No token yet OR token expires within refresh_skew
        return (not self._token) or (time.time() >= (self._expires_at - self.refresh_skew))

    def _request_token(self) -> Tuple[str, float]:
        """
        Request a new token from the OAuth server.
        Uses form-encoded body per spec; client auth via HTTP Basic.
        Returns: (access_token, absolute_expiry_timestamp)
        """
        data = {"grant_type": "client_credentials"}
        if self.scope:
            data["scope"] = self.scope  # space-separated string

        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = requests.post(
                    self.token_url,
                    data=data,  # application/x-www-form-urlencoded
                    auth=(self.client_id, self.client_secret),  # HTTP Basic
                    timeout=self.timeout,
                )
                # Retry on 5xx and 429 (rate limit)
                if resp.status_code in (429,) or resp.status_code >= 500:
                    raise OAuthError(f"Auth server {resp.status_code}: {resp.text[:200]}")

                resp.raise_for_status()
                body = resp.json()
                token = body.get("access_token")
                token_type = (body.get("token_type") or "Bearer").lower()
                expires_in = float(body.get("expires_in", 3600))

                if not token:
                    raise OAuthError(f"Token missing in response: {body}")
                if token_type != "bearer":
                    # Not fatal, but good hygiene to assert expectations
                    raise OAuthError(f"Unexpected token_type: {token_type}")

                return token, time.time() + expires_in

            except Exception as e:
                last_exc = e
                if attempt < self.max_retries:
                    time.sleep(0.5 * (attempt + 1))  # simple linear backoff
                else:
                    break

        raise OAuthError(f"Failed to obtain token: {last_exc}") from last_exc

    def get_token(self) -> str:
        if self._needs_refresh():
            token, exp = self._request_token()
            self._token, self._expires_at = token, exp
        # mypy/pyright: we know _token is set at this point
        return self._token  # type: ignore[return-value]

    def attach(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = _attach(headers)
        headers["Authorization"] = f"Bearer {self.get_token()}"
        return headers


def redact(token: Optional[str], keep: int = 6) -> str:
    """Return a safe preview for logs."""
    if not token:
        return "<none>"
    if len(token) <= keep * 2:
        return token[:keep] + "..."
    return token[:keep] + "..." + token[-keep:]


def apply_auth(headers: Optional[Dict[str, str]], auth) -> Dict[str, str]:
    """
    Generic helper: given any auth object with .attach(headers),
    return headers with credentials attached.
    """
    headers = _attach(headers)
    return auth.attach(headers)
