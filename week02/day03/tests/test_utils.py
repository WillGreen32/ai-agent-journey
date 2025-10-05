from src.utils import slugify, parse_date

def test_slugify():
    assert slugify(" Hello, World! ") == "hello-world"

def test_parse_date():
    assert parse_date("2025-10-02").year == 2025
