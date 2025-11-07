# src/functions/web_search.py
# Mock search: returns canned answers so you can test without internet/API.

schema = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Return a cached fact for a query (mock search).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to look up"}
            },
            "required": ["query"],
            "additionalProperties": False
        }
    }
}

_MOCK_DB = {
    "population of japan": "Approximately 125,000,000",
    "openai": "OpenAI develops advanced AI models.",
    "python": "Python is a versatile programming language."
}

def run(query: str):
    key = query.strip().lower()
    return _MOCK_DB.get(key, "No cached results found.")
