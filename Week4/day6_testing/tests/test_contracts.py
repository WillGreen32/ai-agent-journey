import json
from jsonschema import validate

def test_validate_github_user_golden():
    # Define the expected schema (the contract)
    schema = {
        "type": "object",
        "properties": {
            "login": {"type": "string"},
            "id": {"type": "integer"},
            "html_url": {"type": "string"},
        },
        "required": ["login", "id"]
    }

    # Load your golden file
    with open("tests/data/github_user_golden.json") as f:
        golden = json.load(f)

    # Validate the golden data against the schema
    validate(instance=golden, schema=schema)
