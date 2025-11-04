# src/structured/json_handler.py
"""
Structured JSON Helper:
- request JSON-only replies from the model (response_format = json_object)
- validate against a JSON schema (jsonschema library)
- safe retries for transient errors
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional

import jsonschema
import openai as openai_errors  # for exception types
from openai import OpenAI

# --- Config ---
RETRY_MAX = 2
RETRY_SLEEP_BASE = 1.0  # seconds

client = OpenAI()

def _retry_sleep(attempt: int) -> None:
    time.sleep(RETRY_SLEEP_BASE * (2 ** attempt))

def get_structured_response(
    prompt: str,
    model: str = "gpt-4o-mini",
) -> Dict[str, Any]:
    """
    Ask the model for JSON only. Returns a Python dict (parsed JSON).
    """
    for attempt in range(RETRY_MAX + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0  # deterministic for extraction
            )
            raw = resp.choices[0].message.content
            return json.loads(raw)
        except (openai_errors.RateLimitError, openai_errors.APIError, json.JSONDecodeError) as e:
            if attempt < RETRY_MAX:
                _retry_sleep(attempt)
                continue
            raise

def validate_json(
    data: Dict[str, Any],
    schema: Dict[str, Any],
) -> None:
    """
    Validate data against schema. Raises jsonschema.ValidationError if invalid.
    """
    jsonschema.validate(instance=data, schema=schema)

def get_validated_json(
    prompt: str,
    schema: Dict[str, Any],
    model: str = "gpt-4o-mini",
    max_retries: int = 1,
) -> Dict[str, Any]:
    """
    Request JSON, then validate. If validation fails, retry a few times
    with a gentle "fix" nudge.
    """
    tries = 0
    last_err: Optional[Exception] = None

    base_prompt = prompt
    while tries <= max_retries:
        try:
            data = get_structured_response(base_prompt, model=model)
            validate_json(data, schema)
            return data
        except jsonschema.ValidationError as e:
            last_err = e
            # Nudge the model to fix the structure
            base_prompt = (
                f"{prompt}\n\n"
                "IMPORTANT: Return EXACTLY the required JSON keys and types. "
                "No extra fields. Valid JSON only."
            )
        except Exception as e:
            last_err = e
        tries += 1

    # If we reach here, we failed
    raise RuntimeError(f"Validation failed after retries: {last_err}")
