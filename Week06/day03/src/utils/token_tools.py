"""
Token & Cost Tools
------------------
Simple utilities to count tokens, estimate cost, and chunk long text safely.

Plain-language ideas:
- Tokens are tiny pieces of text the model reads.
- Counting tokens helps you avoid overflows and control cost.
- Chunking splits long text into smaller, token-safe pieces.
"""

from __future__ import annotations
from typing import List, Dict
import re

import tiktoken


# ---------------------------
# 0) Internal helpers
# ---------------------------

# Known pricing (USD per 1,000 tokens). Update these if OpenAI pricing changes.
_PRICING: Dict[str, Dict[str, float]] = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.0005, "output": 0.002},
}

def get_pricing(model: str) -> Dict[str, float]:
    """
    Return pricing dict for the model or raise a friendly error with guidance.
    """
    if model not in _PRICING:
        # Tip the user to add their model if missing
        raise KeyError(
            f"[token_tools] Pricing for model '{model}' not found. "
            f"Add it to _PRICING in token_tools.py like:\n"
            f"_PRICING['{model}'] = {{'input': INPUT_RATE, 'output': OUTPUT_RATE}}"
        )
    return _PRICING[model]


def safe_encoding_for_model(model: str):
    """
    Get a tokenizer for the given model. If unknown, fall back to cl100k_base
    (works well for modern GPT-4/GPT-3.5 style models).
    """
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback used across many models
        return tiktoken.get_encoding("cl100k_base")


# ---------------------------
# 1) Public API
# ---------------------------

def count_tokens(model: str, text: str) -> int:
    """
    Return token count for the given model/text.

    Year-6 language:
    - We cut the text into tiny pieces (tokens) using the model's own scissors (tokenizer).
    - We count how many pieces there are.
    """
    enc = safe_encoding_for_model(model)
    return len(enc.encode(text or ""))


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int = 0) -> float:
    """
    Estimate $ cost for this request using per-1,000 token rates.

    Cost = ((prompt_tokens * input_rate) + (completion_tokens * output_rate)) / 1000
    """
    rates = get_pricing(model)
    total = ((prompt_tokens * rates["input"]) + (completion_tokens * rates["output"])) / 1000.0
    # round for nice display; keep raw float accuracy for internal math if you like
    return round(total, 6)


def estimate_cost_for_text(model: str, text: str, expected_completion_tokens: int = 0) -> float:
    """
    Convenience: count input tokens for `text`, then estimate cost including an
    expected completion size.
    """
    pt = count_tokens(model, text)
    return estimate_cost(model, pt, expected_completion_tokens)


def chunk_text_by_tokens(
    text: str,
    max_tokens: int,
    model: str = "gpt-4o",
) -> List[str]:
    """
    Split `text` into chunks each <= max_tokens (by token count), using sentence boundaries.

    Simple approach (good enough for most cases):
    1) Split by sentences with a regex that respects common punctuation.
    2) Add sentences to a chunk until the next sentence would push it over `max_tokens`.
    3) Start a new chunk and continue.

    Notes:
    - We avoid cutting sentences in half (keeps meaning intact).
    - If a single sentence is longer than `max_tokens`, we hard-split it by tokens.

    Parameters
    ----------
    text : str
        The document to split.
    max_tokens : int
        The token budget for each chunk (e.g., 300).
    model : str
        The model whose tokenizer should be used (affects counts).

    Returns
    -------
    List[str]
        A list of token-safe chunks.
    """
    if max_tokens <= 0:
        raise ValueError("max_tokens must be > 0")

    enc = safe_encoding_for_model(model)
    cleaned = (text or "").strip()
    if not cleaned:
        return []

    # --- Sentence splitting ---
    # This regex splits on ., !, ? followed by space/newline, keeping punctuation with the sentence.
    # It won't be perfect (abbreviations like "e.g."), but it's a practical baseline.
    sentence_pattern = re.compile(r'(?<=\.|\?|!)\s+')
    sentences = sentence_pattern.split(cleaned)

    chunks: List[str] = []
    current: str = ""

    def token_len(s: str) -> int:
        return len(enc.encode(s))

    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue

        # If a single sentence is already too long, we hard-split by tokens.
        if token_len(sent) > max_tokens:
            token_ids = enc.encode(sent)
            start = 0
            while start < len(token_ids):
                end = min(start + max_tokens, len(token_ids))
                piece = enc.decode(token_ids[start:end]).strip()
                if piece:
                    # Flush current if it has content
                    if current:
                        chunks.append(current.strip())
                        current = ""
                    chunks.append(piece)
                start = end
            continue

        candidate = (f"{current} {sent}".strip()) if current else sent
        if token_len(candidate) <= max_tokens:
            current = candidate
        else:
            # flush current, start with this sentence
            if current:
                chunks.append(current.strip())
            current = sent

    if current:
        chunks.append(current.strip())

    return chunks
