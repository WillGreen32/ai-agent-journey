# src/embeddings/embedding_engine.py
from __future__ import annotations

import json
import os
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import numpy as np
import openai as openai_errors           # for exception types when online
from openai import OpenAI                # for real client (only used if not mock)
from .mock_mode import mock_embedding, mock_embeddings

# ---- Config ----
DB_PATH = Path("data/embeddings.db")
DEFAULT_MODEL = os.getenv("EMBEDDINGS_MODEL", "mock-local")  # default to mock for you
BATCH_SIZE = 64
RETRY_MAX = 2
RETRY_SLEEP_BASE = 1.0

# Create the client lazily; it will only be used when not mock
_client: Optional[OpenAI] = None

@dataclass
class SearchResult:
    text: str
    score: float
    metadata: Dict[str, Any]

# ---- Helpers ----
def _sleep(attempt: int) -> None:
    time.sleep(RETRY_SLEEP_BASE * (2 ** attempt))

def _is_mock(model: str) -> bool:
    return model == "mock-local" or os.getenv("EMBEDDINGS_MODE") == "mock"

def _client_instance() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client

# ---- DB ----
def init_db(db_path: Path = DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("""
          CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT UNIQUE,
            metadata TEXT,
            vector TEXT
          );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_text ON embeddings(text);")
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        conn.commit()
    finally:
        conn.close()

# ---- Embeddings ----
def get_embedding(
    text: str,
    model: str = DEFAULT_MODEL,
    normalize_query: bool = False,
) -> List[float]:
    if normalize_query:
        text = text.strip().lower()

    if _is_mock(model):
        return mock_embedding(text)

    # real OpenAI call
    for attempt in range(RETRY_MAX + 1):
        try:
            resp = _client_instance().embeddings.create(input=text, model=model)
            return resp.data[0].embedding
        except (openai_errors.RateLimitError, openai_errors.APIError):
            if attempt < RETRY_MAX:
                _sleep(attempt)
                continue
            raise

def get_embeddings_batch(
    texts: Sequence[str],
    model: str = DEFAULT_MODEL,
    normalize_query: bool = False,
) -> List[List[float]]:
    processed = [t.strip().lower() if normalize_query else t for t in texts]

    if _is_mock(model):
        return mock_embeddings(processed)

    out: List[List[float]] = []
    for i in range(0, len(processed), BATCH_SIZE):
        chunk = processed[i:i + BATCH_SIZE]
        for attempt in range(RETRY_MAX + 1):
            try:
                resp = _client_instance().embeddings.create(input=list(chunk), model=model)
                out.extend([d.embedding for d in resp.data])
                break
            except (openai_errors.RateLimitError, openai_errors.APIError):
                if attempt < RETRY_MAX:
                    _sleep(attempt)
                    continue
                raise
    return out

# ---- Insert with caching ----
def add_text(
    text: str,
    metadata: Optional[Dict[str, Any]] = None,
    model: str = DEFAULT_MODEL,
    db_path: Path = DB_PATH,
    normalize_query: bool = False,
) -> bool:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM embeddings WHERE text=?", (text,))
        if cur.fetchone():
            return False
        emb = get_embedding(text, model=model, normalize_query=normalize_query)
        cur.execute(
            "INSERT INTO embeddings (text, metadata, vector) VALUES (?,?,?)",
            (text, json.dumps(metadata or {}), json.dumps(emb)),
        )
        conn.commit()
        return True
    finally:
        conn.close()

def add_many(
    texts: Sequence[str],
    metadatas: Optional[Sequence[Dict[str, Any]]] = None,
    model: str = DEFAULT_MODEL,
    db_path: Path = DB_PATH,
    normalize_query: bool = False,
) -> int:
    conn = sqlite3.connect(db_path)
    added = 0
    try:
        cur = conn.cursor()
        if not texts:
            return 0

        placeholders = ",".join("?" for _ in texts)
        cur.execute(f"SELECT text FROM embeddings WHERE text IN ({placeholders})", tuple(texts))
        existing = {t for (t,) in cur.fetchall()}

        to_add = [(idx, t) for idx, t in enumerate(texts) if t not in existing]
        if not to_add:
            return 0

        if metadatas is None:
            metadatas = [{} for _ in texts]
        meta_by_idx = {i: m for i, m in enumerate(metadatas)}

        new_texts = [t for _, t in to_add]
        vectors = get_embeddings_batch(new_texts, model=model, normalize_query=normalize_query)

        for (idx, t), vec in zip(to_add, vectors):
            cur.execute(
                "INSERT INTO embeddings (text, metadata, vector) VALUES (?,?,?)",
                (t, json.dumps(meta_by_idx.get(idx, {})), json.dumps(vec)),
            )
            added += 1

        conn.commit()
        return added
    finally:
        conn.close()

# ---- Similarity ----
def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    a_np = np.asarray(a, dtype=np.float32)
    b_np = np.asarray(b, dtype=np.float32)
    denom = float(np.linalg.norm(a_np) * np.linalg.norm(b_np))
    if denom == 0.0:
        return 0.0
    return float(np.dot(a_np, b_np) / denom)

# ---- Query ----
def search_similar(
    query: str,
    top_k: int = 3,
    model: str = DEFAULT_MODEL,
    db_path: Path = DB_PATH,
    normalize_query: bool = False,
    return_metadata: bool = True,
) -> List[SearchResult]:
    q_emb = get_embedding(query, model=model, normalize_query=normalize_query)

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT text, metadata, vector FROM embeddings")
        rows = cur.fetchall()
    finally:
        conn.close()

    scored: List[SearchResult] = []
    for text, meta_json, vec_json in rows:
        vec = json.loads(vec_json)
        score = cosine_similarity(q_emb, vec)
        meta = json.loads(meta_json) if (return_metadata and meta_json) else {}
        scored.append(SearchResult(text=text, score=score, metadata=meta))

    scored.sort(key=lambda r: r.score, reverse=True)
    return scored[:max(1, top_k)]
