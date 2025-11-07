# src/functions/embeddings_lookup.py
# Tiny offline "semantic" lookup using keyword overlap (mock for now).

schema = {
    "type": "function",
    "function": {
        "name": "embeddings_lookup",
        "description": "Search a tiny local knowledge base using simple keyword overlap (mock for embeddings).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "top_k": {"type": "integer", "description": "How many results to return", "default": 3, "minimum": 1, "maximum": 10}
            },
            "required": ["query"],
            "additionalProperties": False
        }
    }
}

# Mini knowledge base (doc_id -> text)
_KB = {
    "ai_agents_intro": "AI agents use tools, memory, and reasoning loops to solve tasks.",
    "python_oop": "Object-oriented programming in Python uses classes and objects.",
    "vector_memory": "Vector databases store embeddings for semantic search and retrieval.",
    "marketing_seo": "SEO improves visibility in search engines with content and links."
}

def _score(query: str, text: str) -> int:
    q = set(query.lower().split())
    t = set(text.lower().split())
    return len(q & t)

def run(query: str, top_k: int = 3):
    scores = [(doc_id, _score(query, text)) for doc_id, text in _KB.items()]
    scores.sort(key=lambda x: x[1], reverse=True)
    results = [{"doc_id": d, "score": s, "text": _KB[d]} for d, s in scores[:top_k]]
    return {"query": query, "results": results}
