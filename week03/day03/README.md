# Day 3 — Regex & Cleaning (Real-World Messes)

This module provides safe, reusable text-cleaning utilities for pipelines.

## Utilities
- `clean_email` — lowercases and strips unwanted chars (pre-clean, not full RFC)
- `clean_phone_au` — normalize to 10-digit AU numbers (handles `+61`)
- `strip_html` — non-greedy tag removal (`<.*?>`)
- `normalize_whitespace` — collapse any whitespace to single spaces + trim
- `standardize_state` — normalize AU state names to standard abbreviations
- `remove_emoji` / `remove_symbols` — helpers used in chain tests

## Run tests
```bash
pytest -q week03/day03/tests
