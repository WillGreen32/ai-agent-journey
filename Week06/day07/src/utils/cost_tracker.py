# src/utils/cost_tracker.py
from datetime import datetime

def track_cost(model: str, tokens: int, extra: dict | None = None):
    """
    Minimal logger stub.
    In Week 7 we'll calculate real token usage from API calls.
    For now, this just prints a cost entry to confirm tracking works.
    """
    entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "model": model,
        "tokens": tokens,
        **(extra or {})
    }
    print("💸 Cost Log:", entry)
    return entry
