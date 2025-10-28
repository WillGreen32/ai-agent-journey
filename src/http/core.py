# src/http/core.py
import os
import requests
from dotenv import load_dotenv

# .env is optional—pass base_url in main.py if you prefer
load_dotenv()
BASE_URL = os.getenv("API_BASE_URL")

class HttpError(Exception):
    """Custom error for HTTP issues"""
    pass

class HttpClient:
    def __init__(self, base_url=BASE_URL, timeout=5):
        if not base_url:
            raise ValueError("Base URL is required. Set API_BASE_URL in .env or pass base_url.")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def _join(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    def _handle_response(self, response):
        if not response.ok:
            body_preview = (response.text or "")[:200].replace("\n", " ")
            raise HttpError(f"Error {response.status_code}: {body_preview}")
        try:
            return response.json()
        except ValueError:
            return response.text

    def get(self, path, params=None, timeout=None):
        url = self._join(path)
        response = self.session.get(url, params=params, timeout=timeout or self.timeout)
        return self._handle_response(response)

    def post(self, path, data=None, timeout=None):
        url = self._join(path)
        response = self.session.post(url, json=data, timeout=timeout or self.timeout)
        return self._handle_response(response)
