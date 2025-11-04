# src/embeddings/embedding_engine.py
"""
Offline Embedding Engine (mock version)
Uses a local fake embedding generator instead of OpenAI's API.
"""

import json, sqlite3
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import numpy as np

# Import our mock client instead of OpenAI
from src.embeddings.mock_openai import MockEmbeddingClient

DB_PATH = Path("data/embeddings.db")
DEFAULT_MODEL = "text-embedding-3-small"
client = MockEmbeddingClient(dim=1536)

# ---------- DB ----------
def init_db(db_path: Path = DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
      CREATE TABLE IF NOT EXISTS embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT UNIQUE,
        metadata TEXT,
        vector TEXT
      );
    """)
    conn.commit(); conn.close()

# ---------- Embeddings ----------
def get_embedding(text: str, model: str = DEFAULT_MODEL) -> List[float]:
    resp = client.embeddings_create(input=text, model=model)
    return resp["data"][0]["embedding"]

# ---------- Insert with caching ----------
def add_text(text: str, metadata: Optional[Dict[str, Any]] = None,
             db_path: Path = DB_PATH) -> bool:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id FROM embeddings WHERE text=?", (text,))
    if cur.fetchone():
        conn.close(); return False

    emb = get_embedding(text)
    cur.execute(
        "INSERT INTO embeddings (text, metadata, vector) VALUES (?,?,?)",
        (text, json.dumps(metadata or {}), json.dumps(emb))
    )
    conn.commit(); conn.close()
    return True

def add_many(texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None,
             db_path: Path = DB_PATH) -> int:
    metadatas = metadatas or [{} for _ in texts]
    added = 0
    for t, m in zip(texts, metadatas):
        added += 1 if add_text(t, m, db_path) else 0
    return added

# ---------- Cosine similarity ----------
def cosine_similarity(a: List[float], b: List[float]) -> float:
    a_np, b_np = np.array(a), np.array(b)
    denom = np.linalg.norm(a_np) * np.linalg.norm(b_np)
    return float(np.dot(a_np, b_np) / denom) if denom else 0.0

# ---------- Search ----------
def search_similar(query: str, top_k: int = 3, db_path: Path = DB_PATH) -> List[Tuple[str, float]]:
    q_emb = get_embedding(query)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT text, vector FROM embeddings")
    rows = cur.fetchall(); conn.close()

    scored = []
    for text, vec_json in rows:
        vec = json.loads(vec_json)
        score = cosine_similarity(q_emb, vec)
        scored.append((text, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:max(1, top_k)]
