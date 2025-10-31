import requests, time

class RetryError(Exception):
    pass

class GitHubClient:
    def __init__(self, auth_token, base_url="https://api.github.com", retries=3, backoff=0.1):
        self.base_url = base_url
        self.retries = retries
        self.backoff = backoff
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {auth_token}",
            "Accept": "application/vnd.github+json"
        })

    def get_user(self, username):
        url = f"{self.base_url}/users/{username}"
        for attempt in range(1, self.retries + 1):
            r = self.session.get(url)
            if r.status_code in (500, 429):  # transient errors
                if attempt == self.retries:
                    raise RetryError(f"Failed after {self.retries} attempts ({r.status_code})")
                time.sleep(self.backoff * attempt)
                continue
            return r

import hmac, hashlib

class GitHubClient:
    def __init__(self, auth_token, base_url="https://api.github.com", user_agent="AIVO-GitHubClient/1.0", signing_secret=None):
        self.base_url = base_url
        self.auth_token = auth_token
        self.user_agent = user_agent
        self.signing_secret = signing_secret

        self.session = requests.Session()
        self.session.headers.update(self._build_headers())

    def _build_headers(self):
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": self.user_agent,
        }
        return headers

    def _build_signed_headers(self, body: bytes) -> dict:
        """
        Optional: attach a reproducible HMAC signature for POST/PUT bodies.
        """
        headers = self._build_headers()
        if self.signing_secret:
            sig = hmac.new(self.signing_secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
            headers["X-Signature-SHA256"] = sig
        return headers
