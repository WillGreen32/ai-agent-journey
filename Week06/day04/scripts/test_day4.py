# scripts/test_day4.py
from __future__ import annotations

import json

from src.structured.json_handler import get_validated_json
from src.embeddings.embedding_engine import (
    init_db, add_text, add_many, search_similar
)

# ---- 1) Structured JSON + validation ----
schema = {
    "type": "object",
    "properties": {
        "product_name": {"type": "string"},
        "price": {"type": "number"},
        "currency": {"type": "string"}
    },
    "required": ["product_name", "price"]
}

prompt = "Extract product_name, price, currency from: 'Nike Air Zoom costs $149.99 USD'."

print("\n=== Structured JSON test ===")
data = get_validated_json(prompt, schema)
print("Validated:", data)

# ---- 2) Embeddings store + search ----
print("\n=== Embeddings test ===")
init_db()

add_text("Nike Air Zoom running shoe", {"brand": "Nike"})
add_text("Adidas Ultraboost daily trainer", {"brand": "Adidas"})
add_many(
    ["New Balance 990v5 lifestyle", "Asics Gel-Kayano stability", "Nike Pegasus road shoe"],
    [{"brand": "New Balance"}, {"brand": "Asics"}, {"brand": "Nike"}]
)

hits = search_similar("best nike zoom for running", top_k=3)
for i, h in enumerate(hits, 1):
    print(f"{i}. score={h.score:.3f} | text={h.text} | meta={h.metadata}")
