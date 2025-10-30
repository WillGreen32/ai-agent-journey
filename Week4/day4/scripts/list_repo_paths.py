# scripts/list_repo_paths.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.openapi.spec_utils import load_openapi_from_url, iter_paths

SPEC_URL = "https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.yaml"

def main():
    spec = load_openapi_from_url(SPEC_URL)
    print("🔎 GitHub repo-related endpoints:")
    for p in iter_paths(spec, contains="repos"):
        print(p)

if __name__ == "__main__":
    main()
