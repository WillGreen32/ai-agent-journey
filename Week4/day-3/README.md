# Day 3 — Robustness: Retries, Backoff, Idempotency, Rate Limits

## What’s inside
- `src/http/` — reusable helpers for:
  - `exponential_backoff_retry` (+ jitter)
  - `handle_rate_limit` (429 Retry-After)
  - Idempotency key utils + local cache
  - `client.post_idempotent()` example wrapper
- `tests/http/` — sanity tests to validate behavior
- `examples/demo_post.py` — quick demo runner

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
python examples/demo_post.py
