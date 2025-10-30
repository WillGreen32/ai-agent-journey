from src.http.pagination import paginate_cursor, paginate_page_limit
from src.cache.simple_cache import get_with_etag
from src.validate.schema_validator import validate_response

def smoke():
    # 1) ETag cache sanity (GitHub supports ETag)
    gh = "https://api.github.com/repos/openai/openai-python"
    d1 = get_with_etag(gh)
    d2 = get_with_etag(gh)  # should hit 304 under the hood and return cached

    # 2) Minimal schema check
    schema = {
        "type": "object",
        "properties": {"id": {"type": "integer"}, "name": {"type": "string"}},
        "required": ["id", "name"]
    }
    assert validate_response(d2, schema, label="GitHub repo")

    print("✅ Smoke tests passed.")



import requests
from src.validate.schema_validator import validate_response

url = "https://api.github.com/repos/openai/openai-python"
data = requests.get(url, headers={"User-Agent":"Day4-Client"}).json()

schema = {
  "type":"object",
  "properties":{"id":{"type":"integer"}, "name":{"type":"string"}},
  "required":["id","name"]
}
validate_response(data, schema, label="GitHub repo")  # should print ✅


if __name__ == "__main__":
    smoke()

