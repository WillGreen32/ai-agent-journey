import pytest, responses
from client.github import GitHubClient, RetryError

@responses.activate
def test_retry_on_500(monkeypatch):
    """
    Simulate a 500 Internal Server Error and ensure retry logic kicks in.
    """
    # Arrange: create client
    client = GitHubClient("testtoken", retries=3, backoff=0)

    # Mock three failing calls
    for _ in range(3):
        responses.add(
            responses.GET,
            "https://api.github.com/users/octocat",
            status=500
        )

    # Act + Assert: expect RetryError after 3 attempts
    with pytest.raises(RetryError):
        client.get_user("octocat")

    # Verify that the API was called three times
    assert len(responses.calls) == 3

@responses.activate
def test_retry_on_rate_limit(monkeypatch):
    """
    Simulate GitHub 429 Too Many Requests and ensure retry logic handles it.
    """
    client = GitHubClient("testtoken", retries=2, backoff=0)

    # GitHub returns 429 (rate limited)
    for _ in range(2):
        responses.add(
            responses.GET,
            "https://api.github.com/users/octocat",
            status=429,
            headers={"Retry-After": "1"}
        )

    with pytest.raises(RetryError):
        client.get_user("octocat")

    assert len(responses.calls) == 2
