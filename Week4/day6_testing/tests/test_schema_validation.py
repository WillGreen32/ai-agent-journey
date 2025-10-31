from jsonschema import validate, ValidationError

def test_basic_schema_validation():
    # Define the "contract" — what we expect data to look like
    schema = {
        "type": "object",
        "properties": {
            "login": {"type": "string"},
            "id": {"type": "integer"},
            "followers": {"type": "integer"}
        },
        "required": ["login", "id"]
    }

    # Example 1: Correct data (matches schema)
    good = {"login": "octocat", "id": 1, "followers": 100}

    # Example 2: Incorrect data (wrong types)
    bad  = {"login": 123, "id": "oops"}  # fails both type checks

    # ✅ Should pass
    validate(instance=good, schema=schema)

    # ❌ Should fail
    try:
        validate(instance=bad, schema=schema)
        assert False, "Bad data should raise ValidationError"
    except ValidationError:
        assert True
