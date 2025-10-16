from src.pipeline import validator

def test_flag_invalid_emails(sample_df):
    df = validator.flag_invalid_emails(sample_df.copy())
    assert "email_valid" in df.columns
    assert df["email_valid"].tolist() == [True, True, False]

import pandas as pd
import pytest
from src.pipeline import validator

def test_flag_invalid_emails(sample_df):
    df = validator.flag_invalid_emails(sample_df.copy())
    assert "email_valid" in df.columns
    # sample_df includes a bad email -> [True, True, False]
    assert df["email_valid"].tolist() == [True, True, False]

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
    assert out.loc[0, "email_valid"] is valid
