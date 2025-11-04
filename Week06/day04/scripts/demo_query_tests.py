# scripts/demo_query_tests.py
from __future__ import annotations
import _pathfix  # keeps imports working

from src.embeddings.embedding_engine import init_db, add_many, search_similar

def pp(title: str, query: str, top_k: int = 3):
    print(f"\n--- {title} ---")
    print(f"Query: {query}")
    hits = search_similar(query, top_k=top_k, model="mock-local")
    for i, h in enumerate(hits, 1):
        print(f"{i}. score={h.score:.3f} | {h.text}")

def main():
    init_db()

    # Seed corpus (same as the previous demo + a few near-duplicates)
    texts = [
        "AI will transform marketing roles and workflows.",
        "Machine learning enables highly targeted ad campaigns.",
        "Cooking pasta requires boiling salted water.",
        "Neural networks can classify images and speech.",
        "Good sleep improves cognitive performance and memory.",
        "Artificial intelligence will change how marketing teams operate.",
        "Targeted advertising campaigns are powered by machine learning.",
        "Boil water with salt before adding pasta for best texture."
    ]
    add_many(texts, model="mock-local")

    # On-topic queries
    pp("Ads / Marketing 1", "How will AI change marketing jobs?", top_k=3)
    pp("Ads / Marketing 2", "machine learning in advertising", top_k=3)

    # Near duplicate testing
    pp("Near-duplicate check", "Will AI transform marketing roles?", top_k=3)

    # Off-topic query (should produce low scores for marketing items)
    pp("Off-topic", "best ways to cook spaghetti", top_k=3)

if __name__ == "__main__":
    main()
