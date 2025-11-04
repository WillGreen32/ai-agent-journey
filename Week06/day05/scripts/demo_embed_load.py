# scripts/demo_embed_load.py
import os, sys

# Make "src" importable when running from day05 folder
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.embeddings.embedding_engine import init_db, add_many, search_similar

def pretty(results, k=3):
    for i, (text, score) in enumerate(results[:k], start=1):
        print(f"{i:>2}. {score:0.3f}  {text}")

if __name__ == "__main__":
    init_db()

    texts = [
        "AI will transform marketing roles and workflows.",
        "Machine learning enables highly targeted ad campaigns.",
        "Cooking pasta requires boiling salted water.",
        "Neural networks can classify images and speech.",
        "Good sleep improves cognitive performance and memory.",
        "AI will change marketing jobs and internal processes."
    ]
    added = add_many(texts)
    print(f"Inserted: {added} new rows")

    tests = [
        ("How does AI affect advertising?", 3),
        ("What improves memory and thinking?", 3),
        ("Best way to cook spaghetti?", 3),
        ("Image recognition with neural nets", 3),
        # near-duplicate probe:
        ("Change in marketing roles from AI", 4),
        # clearly off-topic:
        ("The price of houses on Mars", 3),
    ]

    for q, k in tests:
        print(f"\nQuery: {q}\n")
        res = search_similar(q, top_k=k)
        pretty(res, k=k)
