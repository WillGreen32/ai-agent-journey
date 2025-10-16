# ==============================
# conftest.py — Week 3 Day 6
# ==============================

import sys
from pathlib import Path
import pytest
import pandas as pd

# -------------------------------------------------
# 1) Make 'src' importable (add .../day06 to sys.path)
# -------------------------------------------------
DAY06_DIR = Path(__file__).resolve().parents[1]  # .../week03/day06
if str(DAY06_DIR) not in sys.path:
    sys.path.insert(0, str(DAY06_DIR))  # lets 'from src....' work

# -------------------------------------------------
# 2) Determinism helper
# -------------------------------------------------
from src.pipeline.utils import set_global_determinism  # requires src/pipeline/utils.py

# -------------------------------------------------
# 3) Autouse fixture: deterministic + temp-dir sandbox
# -------------------------------------------------
@pytest.fixture(autouse=True)
def ensure_clean_reproducible_env(tmp_path):
    """
    Runs automatically before every test:
      - Sets global random seeds (42)
      - Provides an isolated temp directory (tmp_path)
    """
    set_global_determinism(42)
    return tmp_path

# -------------------------------------------------
# 4) Sample dataframe fixture for unit tests
# -------------------------------------------------
@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "first_name": ["Ana", "BOB", None],
        "last_name":  ["Smith", "jones", "Lee"],
        "email":      ["ana@example.com", "bob@EXAMPLE.com", "bademail"],
        "state":      ["VIC", "NSW", "VIC"],
        "signup_date":["2024-01-10", "2024-02-02", "2024-01-31"]
    })
