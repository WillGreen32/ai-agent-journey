import responses
import requests

@responses.activate
def test_basic_mock():
    # 1. Tell 'responses' what fake call we expect
    responses.add(
        responses.GET,
        "https://api.github.com/users/octocat",
        json={"login": "octocat"},
        status=200,
    )

    # 2. Make the real-looking call (but it won't leave your PC)
    resp = requests.get("https://api.github.com/users/octocat")

    # 3. Check that our fake response returned correctly
    assert resp.status_code == 200
    assert resp.json()["login"] == "octocat"
