import responses, requests

@responses.activate
def test_mock_403_forbidden():
    responses.add(
        responses.GET,
        "https://api.github.com/user",
        json={"message": "Forbidden"},
        status=403,
    )
    resp = requests.get("https://api.github.com/user")
    assert resp.status_code == 403
    assert resp.json()["message"] == "Forbidden"
