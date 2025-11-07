from typing import Dict

# Small, fake "database" so we can test without the internet
_MOCK_DB: Dict[str, str] = {
    "openai": "OpenAI develops advanced AI models.",
    "python": "Python is a versatile programming language.",
    "60": "Article 60 - European trade law (mock hit).",
}

def web_search(query: str) -> str:
    """
    Mock search tool that returns pre-cached results (offline-safe).

    Args:
        query: the text to look up

    Returns:
        A short description string, or a default 'not found' message.
    """
    if query is None:
        return "No cached results found."
    return _MOCK_DB.get(str(query).lower(), "No cached results found.")
