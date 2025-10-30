from jsonschema import validate, ValidationError  # noqa: F401

def validate_response(data, schema):
    """Validate JSON data against a jsonschema. Raises ValidationError on mismatch."""
    validate(instance=data, schema=schema)
