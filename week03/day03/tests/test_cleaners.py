from clean.cleaners import (
    clean_email, clean_phone_au, strip_html,
    normalize_whitespace, standardize_state
)

def test_clean_email_basic():
    assert clean_email("  TEST@EXAMPLE.com ") == "test@example.com"
    # Note: we pre-clean only; we don't do full RFC validation
    assert clean_email("jane..smith@@gmail.com") == "jane..smith@@gmail.com"

def test_clean_phone_au_formats():
    assert clean_phone_au("+61 (03) 9876 5432") == "0398765432"
    assert clean_phone_au("0499 111 222") == "0499111222"
    assert clean_phone_au("61-499-333-444") == "0499333444"
    assert clean_phone_au("123") == ""  # invalid: not 10 digits

def test_strip_html_non_greedy():
    assert strip_html("<p>A</p><b>B</b>") == "AB"
    assert strip_html("<div><p>Hello</p> <i>W</i></div>") == "Hello W"

def test_normalize_whitespace():
    assert normalize_whitespace("Too     many     spaces") == "Too many spaces"
    assert normalize_whitespace("A\tB \n C") == "A B C"

def test_standardize_state():
    assert standardize_state("victoria") == "VIC"
    assert standardize_state("  new south wales ") == "NSW"
    assert standardize_state("random") == "RANDOM"

def test_mini_chain():
    raw = " <p>HELLO</p>   VIC "
    s = strip_html(raw)                       # " HELLO   VIC "
    s = normalize_whitespace(s)               # "HELLO VIC"
    s = s.lower()                             # "hello vic"
    assert s == "hello vic"

import pytest
from clean.cleaners import clean_phone_au, clean_email

@pytest.mark.parametrize("raw,expected", [
    ("+61 499 333 444", "0499333444"),  # +61 mobile, no trunk
    ("+61 (03) 9876 5432", "0398765432"),  # +61 + area code
    ("0499-333-444", "0499333444"),  # punctuation
    ("(03)98765432", "0398765432"),  # landline compact
    ("", ""), ("foo", ""), ("+44 20 7946 0000", ""),  # not AU, reject
])
def test_phone_param(raw, expected):
    assert clean_phone_au(raw) == expected

@pytest.mark.parametrize("raw,expected", [
    (" A@B.com ", "a@b.com"),
    ("X+y%z@D.co", "x+y%z@d.co"),
    ("inv@lid^char", "inv@lidchar"),
    (None, ""),
    ("", ""),
])
def test_email_param(raw, expected):
    assert clean_email(raw) == expected
