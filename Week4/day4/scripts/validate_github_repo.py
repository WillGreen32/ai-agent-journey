# scripts/validate_github_repo.py
import requests
from src.openapi.spec_utils import load_openapi_from_url, get_response_schema
from src.validate.schema_validator import validate_response

SPEC_URL = "https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.yaml"
PATH = "/repos/{owner}/{repo}"            # target operation
METHOD = "get"
STATUS = "200"
MIME = "application/json"

def main():
    # 1) Load spec
    spec = load_openapi_from_url(SPEC_URL)

    # 2) Extract + dereference response schema for GET /repos/{owner}/{repo}
    schema = get_response_schema(spec, PATH, method=METHOD, status=STATUS, mime=MIME, dereference=True)

    # 3) Fetch live data from GitHub
    url = "https://api.github.com/repos/openai/openai-python"
    headers = {"User-Agent": "Day4-Client/1.0"}
    resp = requests.get(url, headers=headers, timeout=15.0)
    resp.raise_for_status()
    data = resp.json()

    # 4) Validate
    validate_response(data, schema, label="GET /repos/{owner}/{repo}")

    print("🎉 Live GitHub response matches the OpenAPI schema.")

if __name__ == "__main__":
    main()
