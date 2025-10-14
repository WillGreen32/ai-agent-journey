# Make src importable (if you don't have conftest.py)
import sys
from pathlib import Path
THIS = Path(__file__).resolve()
SRC = THIS.parents[1] / "src"
sys.path.insert(0, str(SRC))

from clean.cleaners import (
    strip_html,
    remove_emoji,
    remove_symbols,
    normalize_whitespace as norm_ws,
    clean_phone_au,
)

def test_symbols_allowlist():
    assert remove_symbols("Price: $49!") == "Price $49"

def test_phone_normalize():
    assert clean_phone_au("+61 (03) 9876 5432") == "0398765432"

def test_clean_text_chain():
    raw = "Hi <b>WILL</b> 😊,  call +61 (03) 9876 5432   today!"

    # ---- build the chain (do NOT comment these out) ----
    s1 = strip_html(raw)
    s2 = remove_emoji(s1)
    s3 = remove_symbols(s2)
    s4 = norm_ws(s3).lower()
    # ----------------------------------------------------

    assert "hi will call" in s4
    assert clean_phone_au(raw) == "0398765432"
