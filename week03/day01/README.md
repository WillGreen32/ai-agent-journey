# Day 1 — CSV & JSON I/O System

Reliable, portable file-handling modules for CSV/JSON with UTF-8, BOM safety, and stable schemas.

## Overview
- **Ingest**: Read CSV with `utf-8-sig` (BOM-safe) and correct newline handling.
- **Normalize**: Lowercase + trim headers; trim values.
- **Write**: Save pretty JSON and deterministic CSV (stable column order).

## Usage (inside this project)
```python
from src.io.csv_io import load_csv, save_csv
from src.io.json_io import load_json, save_json

rows = load_csv("data/processed/users.csv")   # list[dict]
save_json("data/processed/users.json", rows)  # pretty UTF-8 JSON
