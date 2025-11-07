from src.functions.embeddings_lookup import embeddings_lookup

def test_returns_string_with_query():
    q = "pricing policy"
    out = embeddings_lookup(q)
    assert isinstance(out, str)
    assert q in out
