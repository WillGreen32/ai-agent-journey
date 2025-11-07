calculator_tool = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Performs basic arithmetic on two numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
                "operator": {"type": "string", "enum": ["+", "-", "*", "/"]}
            },
            "required": ["a", "b", "operator"]
        }
    }
}

web_search_tool = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Returns cached search results for a query (mock, offline-safe).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    }
}

embeddings_lookup_tool = {
    "type": "function",
    "function": {
        "name": "embeddings_lookup",
        "description": "Looks up a query in a mock vector DB (stub for later).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    }
}

# Export list for convenience
tools = [calculator_tool, web_search_tool, embeddings_lookup_tool]
