def web_search(query: str) -> str:
    \"\"\"Mock search tool that returns pre-cached results (safe for offline tests).\"\"\"
    mock_db = {
        "openai": "OpenAI develops advanced AI models.",
        "python": "Python is a versatile programming language.",
        "60": "Article 60 - European trade law (mock hit)."
    }
    return mock_db.get(str(query).lower(), "No cached results found.")
