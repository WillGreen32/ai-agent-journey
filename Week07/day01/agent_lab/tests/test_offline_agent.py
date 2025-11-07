from src.demo.offline_agent import run_offline_agent

def test_offline_calc_only():
    out = run_offline_agent("What is 4 * 7?", verbose=False)
    assert "calculator => 28.0" in out

def test_offline_chain_calc_then_search():
    out = run_offline_agent("What is 12 * 5, then search that number in your knowledge base.", verbose=False)
    assert "calculator => 60.0" in out
    # '60' is a mock hit in the web_search DB
    assert "web_search => Article 60" in out

def test_offline_embeddings_stub():
    out = run_offline_agent("Do an embeddings lookup for 'retrieval strategy'.", verbose=False)
    assert "embeddings_lookup => Mock embedding results for:" in out
