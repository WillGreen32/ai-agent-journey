# src path is handled by conftest.py; if you skipped it, add the sys.path insert here.
from clean.cleaners import clean_email, strip_html, normalize_whitespace

def test_clean_email():
    assert clean_email(" TEST@EXAMPLE.com ") == "test@example.com"

def test_strip_html():
    assert strip_html("<div>Hi</div>") == "Hi"

def test_normalize_whitespace():
    assert normalize_whitespace("Too   many  spaces") == "Too many spaces"
