# Week 4 — Day 1: HTTP Core Wrapper

A tiny, reusable HTTP client built on `requests` with:
- Base URL config (via `.env` or constructor)
- JSON headers by default
- Centralized error handling (`HttpError`)
- Safe JSON decode with text fallback
- Per-request timeout override

## Install
```bash
pip install -r requirements.txt   # or: pip install requests python-dotenv
