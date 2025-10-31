import os
import pytest
import requests

pytestmark = pytest.mark.live  # mark the whole file as "live"

def live_only():
    if os.getenv("RUN_LIVE") != "1":
        pytest.skip("Set RUN_LIVE=1 to enable live tests")

def _headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "AIVO-GitHubClient/1.0 smoke-test"
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def _assert_reasonable_repo_shape(repo):
    # Light-touch checks to avoid brittleness
    assert "id" in repo and isinstance(repo["id"], int)
    assert "name" in repo and isinstance(repo["name"], str)

def test_live_repos_reachable_and_shape_ok():
    live_only()

    url = "https://api.github.com/users/octocat/repos"
    resp = requests.get(url, headers=_headers(), timeout=8)
    assert resp.status_code == 200, f"Unexpected status {resp.status_code}: {resp.text[:200]}"

    data = resp.json()
    assert isinstance(data, list), "Expected a list of repos"

    # If list is non-empty, sanity-check the first item shape (avoid strict contracts in smoke tests)
    if data:
        _assert_reasonable_repo_shape(data[0])

def test_live_rate_limit_endpoint_ok():
    live_only()

    # Very cheap call that proves auth/headers work and shows remaining tokens
    url = "https://api.github.com/rate_limit"
    resp = requests.get(url, headers=_headers(), timeout=5)
    assert resp.status_code == 200
    payload = resp.json()
    assert "resources" in payload and "core" in payload["resources"]
    # Optional sanity: confirm fields exist (avoid asserting exact numbers)
    core = payload["resources"]["core"]
    assert {"limit", "remaining", "reset"}.issubset(core.keys())
