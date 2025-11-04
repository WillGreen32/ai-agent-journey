# src/embeddings/mock_mode.py
"""
Mock embeddings for offline/local testing (no API key needed).

We generate a deterministic vector from text by hashing it and seeding
NumPy's modern RNG (default_rng). Vectors are L2-normalized so cosine
similarity behaves like real embeddings.
"""
from __future__ import annotations
import hashlib
import numpy as np
from typing import List, Sequence

def _seed_from_text(text: str) -> int:
    # Use a 128-bit seed from SHA-256 digest (safe for default_rng / PCG64)
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return int.from_bytes(digest[:16], byteorder="big", signed=False)

def mock_embedding(text: str, dim: int = 384) -> List[float]:
    rng = np.random.default_rng(_seed_from_text(text))
    v = rng.standard_normal(dim, dtype=np.float32)
    # L2 normalize to unit length
    n = float(np.linalg.norm(v))
    if n == 0.0:
        return v.tolist()
    return (v / n).tolist()

def mock_embeddings(texts: Sequence[str], dim: int = 384) -> List[List[float]]:
    return [mock_embedding(t, dim=dim) for t in texts]
