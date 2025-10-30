"""
GitHub API client: auth (auto-detect + sanitize), retries, ETag caching, pagination, error mapping.
"""

from __future__ import annotations
import time
import typing as t
import requests

from src.cache.simple_cache import SimpleCache
from src.http.pagination import parse_link_header
from src.client.http_retry import build_retry_adapter


class GitHubError(Exception):
    def __init__(self, status: int, message: str, doc_url: t.Optional[str] = None):
        super().__init__(f"[{status}] {message}")
        self.status = status
        self.message = message
        self.doc_url = doc_url


def _sanitize_token(token: t.Optional[str]) -> str:
    """
    Strip quotes/whitespace and any accidental 'token ' or 'Bearer ' prefixes
    so we don't send 'token token abc...' by mistake.
    """
    if not token:
        return ""
    tok = token.strip().strip('"').strip("'")
    for prefix in ("token ", "Bearer ", "bearer ", "TOKEN ", "BEARER "):
        if tok.startswith(prefix):
            tok = tok[len(prefix):].strip()
            break
    return tok


class GitHubClient:
    def __init__(
        self,
        auth_token: t.Optional[str] = None,
        base_url: str = "https://api.github.com",
        cache: t.Optional[SimpleCache] = None,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.cache = cache or SimpleCache()

        # Session + retries
        self.session = requests.Session()
        adapter = build_retry_adapter()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.headers.update({
            "Accept": "application/vnd.github+json",
            "User-Agent": "AIAgent-Learning-GitHubClient/1.0",
        })

        # Auth config
        self.auth_token = _sanitize_token(auth_token)
        self._auth_scheme = "token" if self.auth_token else None
        self._auth_failed = False
        self._apply_auth_header()

    def _apply_auth_header(self):
        if self.auth_token and not self._auth_failed:
            self.session.headers["Authorization"] = f"{self._auth_scheme} {self.auth_token}"
        else:
            self.session.headers.pop("Authorization", None)

    def _request(self, method: str, url: str, *, params=None, headers=None) -> requests.Response:
        """
        Make a request with current auth; if 401 and we have a token,
        try switching token->Bearer once. If still 401, disable auth (public mode).
        """
        r = self.session.request(method, url, params=params, headers=headers or {}, timeout=self.timeout)
        if r.status_code == 401 and self.auth_token and not self._auth_failed:
            if self._auth_scheme == "token":
                # try Bearer once
                self._auth_scheme = "Bearer"
                self._apply_auth_header()
                r = self.session.request(method, url, params=params, headers=headers or {}, timeout=self.timeout)
                if r.status_code == 401:
                    # disable auth altogether (public endpoints will still work)
                    self._auth_failed = True
                    self._apply_auth_header()
                    r = self.session.request(method, url, params=params, headers=headers or {}, timeout=self.timeout)
            else:
                # we were already using Bearer; go public
                self._auth_failed = True
                self._apply_auth_header()
                r = self.session.request(method, url, params=params, headers=headers or {}, timeout=self.timeout)
        return r

    def _handle_response(self, response: requests.Response) -> t.Any:
        if response.status_code == 403 and "X-RateLimit-Remaining" in response.headers:
            if response.headers.get("X-RateLimit-Remaining") == "0":
                reset = response.headers.get("X-RateLimit-Reset")
                if reset:
                    wait = max(0, int(reset) - int(time.time()))
                    time.sleep(min(wait, 2))
        if response.status_code >= 400:
            try:
                err = response.json()
                msg = err.get("message") or "HTTP error"
                doc = err.get("documentation_url")
            except ValueError:
                msg, doc = (response.text or "HTTP error"), None
            raise GitHubError(response.status_code, msg, doc)
        if response.status_code == 204:
            return None
        ctype = response.headers.get("Content-Type", "")
        if ctype.startswith("application/json"):
            return response.json()
        return response.text

    # ------------- cache helpers -------------
    def _cache_key(self, url: str, params: t.Optional[dict]) -> str:
        if not params:
            return url
        parts = [f"{k}={params[k]}" for k in sorted(params.keys())]
        return f"{url}?{'&'.join(parts)}"

    def _get_with_cache(self, url: str, params: t.Optional[dict] = None) -> t.Any:
        key = self._cache_key(url, params)
        cached = self.cache.read(key)
        headers = {}
        if cached and cached.get("etag"):
            headers["If-None-Match"] = cached["etag"]
        r = self._request("GET", url, params=params, headers=headers)
        if r.status_code == 304 and cached:
            return cached["data"]
        data = self._handle_response(r)
        etag = r.headers.get("ETag")
        if etag:
            self.cache.write(key, etag, data)
        return data

    # ------------- pagination -------------
    def _paginate(self, url: str, params: t.Optional[dict] = None) -> t.Iterator[t.Any]:
        next_url = url
        next_params = params or {}
        while next_url:
            key = self._cache_key(next_url, next_params)
            cached = self.cache.read(key)
            headers = {}
            if cached and cached.get("etag"):
                headers["If-None-Match"] = cached["etag"]

            r = self._request("GET", next_url, params=next_params, headers=headers)
            if r.status_code == 304 and cached:
                data = cached["data"]
            else:
                data = self._handle_response(r)
                etag = r.headers.get("ETag")
                if etag:
                    self.cache.write(key, etag, data)

            yield data

            links = parse_link_header(r.headers.get("Link", ""))
            if "next" in links:
                next_url = links["next"]["url"]
                next_params = {}
            else:
                next_url = None
                next_params = {}

    # ------------- public API -------------
    def list_repos(self, user: str) -> t.Iterator[dict]:
        url = f"{self.base_url}/users/{user}/repos"
        for page in self._paginate(url):
            if not isinstance(page, list):
                raise ValueError("Expected a list of repositories")
            for repo in page:
                yield repo

    def get_repo(self, user: str, name: str) -> dict:
        url = f"{self.base_url}/repos/{user}/{name}"
        return self._get_with_cache(url)

    def list_commits(self, user: str, name: str, *, sha: t.Optional[str] = None) -> t.Iterator[dict]:
        url = f"{self.base_url}/repos/{user}/{name}/commits"
        params = {"sha": sha} if sha else None
        for page in self._paginate(url, params=params):
            if not isinstance(page, list):
                raise ValueError("Expected a list of commits")
            for commit in page:
                yield commit
