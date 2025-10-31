import responses, requests, json
from client.github import GitHubClient

@responses.activate
def test_pagination_two_pages(monkeypatch):
    """
    Simulate multiple pages of data and confirm client combines them correctly.
    """
    # Arrange
    client = GitHubClient("TESTTOKEN")

    # Two fake pages
    responses.add(
        responses.GET,
        "https://api.github.com/users/octocat/repos?page=1",
        json=[{"id": 1}],
        headers={"Link": '<https://api.github.com/users/octocat/repos?page=2>; rel="next"'},
        status=200,
    )
    responses.add(
        responses.GET,
        "https://api.github.com/users/octocat/repos?page=2",
        json=[{"id": 2}],
        headers={"Link": ''},  # no next page
        status=200,
    )

    # Monkeypatch paginate() so it calls through requests.get()
    def fake_paginate(url, session, cache=None):
        while url:
            r = session.get(url)
            data = r.json()
            yield data
            next_url = None
            link = r.headers.get("Link")
            if link and "rel=\"next\"" in link:
                next_url = link[link.find("<")+1:link.find(">")]
            url = next_url

    monkeypatch.setattr("client.github.paginate", fake_paginate)

    # Act
    pages = list(client.list_repos("octocat"))

    # Assert
    assert len(pages) == 2
    assert pages[0]["id"] == 1
    assert pages[1]["id"] == 2
    assert len(responses.calls) == 2


from jsonschema import validate, ValidationError

@responses.activate
def test_pagination_schema_validation(monkeypatch):
    client = GitHubClient("TESTTOKEN")

    # Two pages with slightly different data (still valid)
    responses.add(
        responses.GET,
        "https://api.github.com/users/octocat/repos?page=1",
        json=[{"id": 1, "name": "hello-world"}],
        headers={"Link": '<https://api.github.com/users/octocat/repos?page=2>; rel="next"'},
        status=200,
    )
    responses.add(
        responses.GET,
        "https://api.github.com/users/octocat/repos?page=2",
        json=[{"id": 2, "name": "octo-lab"}],
        headers={"Link": ''},
        status=200,
    )

    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
        },
        "required": ["id"],
    }

    def fake_paginate(url, session, cache=None):
        while url:
            r = session.get(url)
            yield r.json()
            next_url = None
            link = r.headers.get("Link")
            if link and "rel=\"next\"" in link:
                next_url = link[link.find("<")+1:link.find(">")]
            url = next_url

    monkeypatch.setattr("client.github.paginate", fake_paginate)

    pages = list(client.list_repos("octocat"))

    # Validate every item on every page
    for item in pages:
        validate(instance=item, schema=schema)

def test_schema_validation_fails_on_bad_type(monkeypatch):
    from jsonschema import validate, ValidationError
    from client.github import GitHubClient

    client = GitHubClient("TESTTOKEN")

    bad_page = [{"id": "WRONG_TYPE"}]

    schema = {
        "type": "object",
        "properties": {"id": {"type": "integer"}},
        "required": ["id"]
    }

    try:
        validate(instance=bad_page[0], schema=schema)
        assert False, "Should have raised ValidationError for wrong type"
    except ValidationError:
        assert True
