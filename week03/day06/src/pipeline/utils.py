# src/pipeline/utils.py
import os, random, numpy as np, time, logging
from functools import wraps
from typing import Callable, Any, Optional

# ---------- Determinism ----------
def set_global_determinism(seed: int = 42) -> None:
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)

# ---------- Logging ----------
def configure_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configure root logger once. Level = DEBUG|INFO|WARNING|ERROR.
    If log_file is provided, logs go to both console and file.
    """
    level_num = getattr(logging, level.upper(), logging.INFO)
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(
        level=level_num,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
        force=True,  # override prior config (great for tests/CLI)
    )

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

# ---------- Timing ----------
def timed(name: Optional[str] = None, log_level: int = logging.INFO) -> Callable:
    """
    Decorator to log wall-clock runtime. Usage:
    @timed()           -> logs function name
    @timed("report")   -> logs custom name
    """
    def deco(fn: Callable) -> Callable:
        lbl = name or fn.__name__
        logger = get_logger(lbl)
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any):
            t0 = time.time()
            try:
                return fn(*args, **kwargs)
            finally:
                elapsed = time.time() - t0
                logger.log(log_level, f"{lbl} ran in {elapsed:.2f}s")
        return wrapper
    return deco
import hashlib
import pandas as pd
from pathlib import Path
from typing import Iterable, Optional

# ---------- Canonicalization ----------

def _canonicalize_df(
    df: pd.DataFrame,
    sort_by: Optional[Iterable[str]] = None,
    float_decimals: int = 6,
    na_rep: str = ""
) -> pd.DataFrame:
    """
    Return a deterministic version of df:
    - Sort columns alphabetically (stable schema)
    - Optionally sort rows by `sort_by` (or all columns if None)
    - Round floats
    - Normalize NaNs
    """
    # 1) stable column order
    df2 = df.copy()
    df2 = df2.reindex(sorted(df2.columns), axis=1)

    # 2) float formatting
    float_cols = df2.select_dtypes(include="number").columns
    if len(float_cols):
        df2[float_cols] = df2[float_cols].round(float_decimals)

    # 3) stable row order
    if sort_by is None:
        sort_by = list(df2.columns)
    if len(sort_by):
        df2 = df2.sort_values(list(sort_by), kind="mergesort").reset_index(drop=True)

    # 4) consistent NA representation for serialization
    df2 = df2.fillna(na_rep)

    return df2

def _csv_bytes(
    df: pd.DataFrame,
    float_decimals: int = 6,
    sort_by: Optional[Iterable[str]] = None
) -> bytes:
    df2 = _canonicalize_df(df, sort_by=sort_by, float_decimals=float_decimals)
    # Important: fixed newline + no index to keep bytes stable
    csv = df2.to_csv(index=False, lineterminator="\n")
    return csv.encode("utf-8")

# ---------- File/folder hashing ----------

def file_hash_csv(path: Path, sort_by: Optional[Iterable[str]] = None, float_decimals: int = 6) -> str:
    """Canonicalize CSV then SHA256 hash."""
    df = pd.read_csv(path)
    data = _csv_bytes(df, float_decimals=float_decimals, sort_by=sort_by)
    return hashlib.sha256(data).hexdigest()

def file_hash_raw(path: Path) -> str:
    """Hash raw bytes (useful for parquet, images, etc)."""
    b = Path(path).read_bytes()
    return hashlib.sha256(b).hexdigest()

def folder_hash_csv(folder: Path, pattern: str = "*.csv") -> str:
    """Hash multiple CSVs deterministically (name + content)."""
    h = hashlib.sha256()
    for p in sorted(Path(folder).rglob(pattern)):
        h.update(p.as_posix().encode("utf-8"))             # filename matters
        h.update(file_hash_csv(p).encode("utf-8"))          # canonical content
    return h.hexdigest()

import os, random, numpy as np

def set_global_determinism(seed: int = 42) -> None:
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)

# src/pipeline/utils.py (append)
import hashlib, pandas as pd
from pathlib import Path
from typing import Iterable, Optional

def _canonicalize_df(
    df: pd.DataFrame,
    sort_by: Optional[Iterable[str]] = None,
    float_decimals: int = 6,
    na_rep: str = ""
) -> pd.DataFrame:
    df2 = df.copy()
    df2 = df2.reindex(sorted(df2.columns), axis=1)      # stable column order
    num = df2.select_dtypes(include="number").columns
    if len(num): df2[num] = df2[num].round(float_decimals)
    if sort_by is None: sort_by = list(df2.columns)
    if len(sort_by): df2 = df2.sort_values(sort_by, kind="mergesort").reset_index(drop=True)
    return df2.fillna(na_rep)                            # normalize NA

def _csv_bytes(df: pd.DataFrame, float_decimals=6, sort_by=None) -> bytes:
    df2 = _canonicalize_df(df, sort_by=sort_by, float_decimals=float_decimals)
    return df2.to_csv(index=False, lineterminator="\n").encode("utf-8")

def file_hash_csv(path: Path, sort_by=None, float_decimals=6) -> str:
    df = pd.read_csv(path)
    data = _csv_bytes(df, float_decimals=float_decimals, sort_by=sort_by)
    return hashlib.sha256(data).hexdigest()
