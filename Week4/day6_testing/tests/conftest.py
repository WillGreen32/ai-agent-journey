import pytest
from client.github import GitHubClient

@pytest.fixture
def github_client():
    return GitHubClient(auth_token="TESTTOKEN")
