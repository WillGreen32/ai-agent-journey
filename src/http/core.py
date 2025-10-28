from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = (os.getenv("API_BASE_URL") or "").rstrip("/")
TIMEOUT  = float(os.getenv("API_TIMEOUT_SECONDS", "5"))
RETRIES  = int(os.getenv("API_RETRY_ATTEMPTS", "3"))

class HttpError(Exception):
    """Base exception for HTTP client errors."""

class HttpClient:
    """Tiny scaffold; we’ll implement methods next."""
    def __init__(self, base_url: str | None = None, timeout: float | None = None, retry_attempts: int | None = None):
        if not (base_url or BASE_URL):
            raise ValueError("base_url is required (or set API_BASE_URL in .env)")
        self.base_url = (base_url or BASE_URL).rstrip("/")
        self.timeout = timeout or TIMEOUT
        self.retry_attempts = retry_attempts or RETRIES

    # placeholder methods (will implement in Build step)
    def get(self, path: str, **kw):  # noqa: D401
        """HTTP GET (to be implemented)."""
        raise NotImplementedError

    def post(self, path: str, data: dict | None = None, **kw):
        raise NotImplementedError
