# src/memory/vector_memory.py
"""
Year-6 explanation:
This file is your agent's "memory library".
- It creates a small database file (SQLite) to store memories.
- It can add new memories (text turned into numbers = embeddings).
- It can find the most similar past memories for a new question.

Technical notes:
- We store embeddings as JSON arrays (list[float]) inside SQLite.
- Retrieval uses cosine similarity (direction closeness).
"""

import sqlite3
import json
from typing import Callable, List, Tuple
import numpy as np
import os

DB_PATH = os.path.join("src", "data", "embeddings.sqlite")

def init_db() -> None:
    """
    Creates the SQLite file + memory table if they don't exist.
    Sets SQLite to WAL mode for safer/faster writes.
    Year-6: Think 'make the notebook and add the first page'.
    """
    # 1) Make sure the folder exists (src/data/)
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # 2) Open (or create) the SQLite file
    conn = sqlite3.connect(DB_PATH)

    try:
        # 3) Safer/faster write mode
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")

        # 4) Create the memory table if missing
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memory(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                embedding TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # 5) (Nice-to-have) small index to speed up age-based ops later
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_memory_created_at ON memory(created_at);"
        )

        conn.commit()
    finally:
        conn.close()

# ---------- Core Ops ----------

def add_memory(text: str, embed_func: Callable[[str], List[float]]) -> None:
    """
    Turn text -> embedding -> store in DB.
    """
    if not text or not text.strip():
        return
    emb = embed_func(text)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO memory (text, embedding) VALUES (?, ?)",
        (text, json.dumps(emb)),
    )
    conn.commit()
    conn.close()

def get_relevant_memories(query: str,
                          embed_func: Callable[[str], List[float]],
                          top_k: int = 3) -> List[str]:
    """
    Return top_k most similar texts by cosine similarity.
    """
    if not query or not query.strip():
        return []

    q = np.array(embed_func(query), dtype=np.float32)

    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT text, embedding FROM memory").fetchall()
    conn.close()

    scored = []
    q_norm = np.linalg.norm(q)
    if q_norm == 0:
        return []

    for text, emb_json in rows:
        e = np.array(json.loads(emb_json), dtype=np.float32)
        e_norm = np.linalg.norm(e)
        if e_norm == 0:
            continue
        cos = float(np.dot(q, e) / (q_norm * e_norm))
        scored.append((cos, text))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in scored[:max(0, top_k)]]

# ---------- Utilities (optional) ----------

def clear_all_memories() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM memory")
    conn.commit()
    conn.close()

# ---------- Simple local embed (for testing only) ----------

def _toy_embed(text: str, dim: int = 64) -> List[float]:
    """
    A tiny, deterministic embedding for local testing (no API needed).
    It hashes chars into a fixed-size vector. Not semantic, just for wiring.
    """
    vec = np.zeros(dim, dtype=np.float32)
    for i, ch in enumerate(text.encode("utf-8")):
        vec[i % dim] += (ch % 13) / 13.0
    # avoid zero vector
    if np.linalg.norm(vec) == 0:
        vec[0] = 1.0
    return vec.tolist()

# ---------- Self-test ----------

def _normalize(vec: np.ndarray) -> np.ndarray:
    """Return a unit-length vector; if zero-length, return the original."""
    norm = np.linalg.norm(vec)
    if norm == 0.0:
        return vec
    return vec / norm


def add_memory(text: str, embed_func: Callable[[str], List[float]]) -> None:
    """
    Save one memory row:
    - text (what to remember)
    - embedding (list[float] from embed_func), stored as JSON
    """
    if not text or not text.strip():
        return
    emb = embed_func(text)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO memory (text, embedding) VALUES (?, ?)",
            (text, json.dumps(emb)),
        )
        conn.commit()
    finally:
        conn.close()

def add_memories(texts: List[str], embed_func: Callable[[str], List[float]]) -> None:
    """
    Bulk insert convenience (faster when seeding many facts).
    """
    if not texts:
        return
    rows = []
    for t in texts:
        if not t or not t.strip():
            continue
        rows.append((t, json.dumps(embed_func(t))))
    if not rows:
        return
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executemany(
            "INSERT INTO memory (text, embedding) VALUES (?, ?)",
            rows,
        )
        conn.commit()
    finally:
        conn.close()

# ---------- Add: read ops (retrieval) ----------

def get_relevant_memories(
    query: str,
    embed_func: Callable[[str], List[float]],
    top_k: int = 3,
) -> List[str]:
    """
    Return only the top_k memory texts most similar to the query (cosine).
    """
    return [t for _, t in get_relevant_with_scores(query, embed_func, top_k)]

def get_relevant_with_scores(
    query: str,
    embed_func: Callable[[str], List[float]],
    top_k: int = 3,
) -> List[Tuple[float, str]]:
    """
    Return list of (score, text) sorted desc by cosine similarity.
    """
    if not query or not query.strip():
        return []

    # Embed + normalize query
    q = np.array(embed_func(query), dtype=np.float32)
    q = _normalize(q)

    # Load all rows
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute("SELECT text, embedding FROM memory").fetchall()
    finally:
        conn.close()

    # Score each row
    scored: List[Tuple[float, str]] = []
    for text, emb_json in rows:
        e = np.array(json.loads(emb_json), dtype=np.float32)
        e = _normalize(e)
        # If either vector is zero, skip
        if e.size == 0 or q.size == 0:
            continue
        # Cosine = dot of normalized vectors
        sim = float(np.dot(q, e))
        scored.append((sim, text))

    # Sort by highest similarity
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[: max(0, top_k)]




if __name__ == "__main__":
    init_db()
    clear_all_memories()

    # Add a few demo memories
    add_memory("User lives in Melbourne.", _toy_embed)
    add_memory("User likes luxury fashion.", _toy_embed)
    add_memory("User wants to target med spas.", _toy_embed)

    # Query
    hits = get_relevant_memories("Where am I based again?", _toy_embed, top_k=2)
    print("Top matches:", hits)
