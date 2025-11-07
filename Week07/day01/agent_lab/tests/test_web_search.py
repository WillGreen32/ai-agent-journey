from src.functions.web_search import web_search

def test_known_hit_is_returned():
    out = web_search("openai")
    assert "OpenAI" in out

def test_unknown_query_uses_default():
    out = web_search("javascript")
    assert "No cached results" in out

def test_query_case_insensitive():
    out1 = web_search("PYTHON")
    out2 = web_search("python")
    assert out1 == out2
