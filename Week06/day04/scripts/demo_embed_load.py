# scripts/demo_embed_load.py
from __future__ import annotations
import _pathfix  # keeps imports working

from src.embeddings.embedding_engine import init_db, add_many, search_similar

# Use mock by default (engine already defaults to mock-local).
# If you ever want real API: pass model="text-embedding-3-small".

def main():
    init_db()

    texts = [
        "AI will transform marketing roles and workflows.",
        "Machine learning enables highly targeted ad campaigns.",
        "Cooking pasta requires boiling salted water.",
        "Neural networks can classify images and speech.",
        "Good sleep improves cognitive performance and memory."
    ]

    added = add_many(texts, model="mock-local")
    print(f"Inserted: {added} new rows")

    query = "How does AI affect advertising?"
    hits = search_similar(query, top_k=2, model="mock-local")

    print(f"\nQuery: {query}")
    for i, h in enumerate(hits, 1):
        print(f"{i}. score={h.score:.3f} | {h.text}")

if __name__ == "__main__":
    main()
