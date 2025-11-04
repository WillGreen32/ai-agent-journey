# Day 4 — Structured Outputs + Embeddings Mini-Stack

This folder contains:
- `src/structured/json_handler.py` → JSON-only responses + schema validation
- `src/embeddings/embedding_engine.py` → SQLite store + cosine top-k search
- `src/embeddings/mock_mode.py` → mock embeddings (no API key needed)
- `scripts/demo_embed_load.py` + `scripts/demo_query_tests.py` → runnable demos

## Quickstart (no API key needed)
```powershell
# 1) Create venv + install
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2) Run demos (uses mock-local by default)
python .\scripts\demo_embed_load.py
python .\scripts\demo_query_tests.py
