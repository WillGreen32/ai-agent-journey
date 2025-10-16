# Week 3 Day 6 — Testing, Reliability & Performance

## Run Tests
pytest -q

## Structure
- Unit tests: cleaners, validator
- Integration: CLI end-to-end
- Golden: output regression
- Smoke/Perf: speed & stability

## Reproducibility
Deterministic seed set to 42 in conftest.py
