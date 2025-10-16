import pandas as pd
import pytest
from src.pipeline import validator

@pytest.mark.parametrize("email,valid", [
    ("simple@example.com", True),
    ("UPPER@EXAMPLE.COM", True),
    ("with+plus@domain.io", True),
    ("first.last@sub.domain.co.uk", True),
    ("no-at-symbol.com", False),
    ("bad@domain", False),
    ("bad@domain.", False),
    ("bad@@example.com", False),
    ("", False),
    (None, False),
])
def test_email_regex_param(email, valid):
    df = pd.DataFrame({"email": [email]})
    out = validator.flag_invalid_emails(df)
    # Convert numpy.bool_ -> Python bool before comparing
    assert bool(out.loc[0, "email_valid"]) == valid
