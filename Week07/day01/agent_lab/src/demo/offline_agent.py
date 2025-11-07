import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


import re
from typing import Dict, Callable, Any, List, Tuple

# Local tools (already built)
from src.functions.calculator import calculator
from src.functions.web_search import web_search
from src.functions.embeddings_lookup import embeddings_lookup

# Map tool name -> function
FUNCTION_MAP: Dict[str, Callable[..., Any]] = {
    "calculator": calculator,
    "web_search": web_search,
    "embeddings_lookup": embeddings_lookup,
}

# -------- Tiny 'planner' (fake model) --------
# Rules:
# 1) If we can find a simple math expression (a op b), call calculator.
# 2) If prompt mentions 'search' or 'look up', call web_search with:
#    - the math result if present, otherwise the remaining text.
# 3) If prompt mentions 'embedding' or 'vector', call embeddings_lookup.

MATH_RE = re.compile(r"(-?\d+(?:\.\d+)?)\s*([+\-*/x÷])\s*(-?\d+(?:\.\d+)?)")

def parse_math(prompt: str) -> Tuple[float, float, str] | None:
    m = MATH_RE.search(prompt)
    if not m:
        return None
    a_s, op, b_s = m.groups()
    # Normalize operator symbols
    op = {"x": "*", "÷": "/"}.get(op, op)
    return float(a_s), float(b_s), op

def wants_search(prompt: str) -> bool:
    p = prompt.lower()
    return any(k in p for k in ["search", "look up", "lookup", "find in", "query"])

def wants_embeddings(prompt: str) -> bool:
    p = prompt.lower()
    return any(k in p for k in ["embedding", "embeddings", "vector", "semantic"])

def plan_actions(prompt: str) -> List[Dict[str, Any]]:
    """
    Returns a list of tool 'actions' the fake model wants to run in order.
    Each action: {"name": <tool_name>, "args": {...}}
    This simulates chaining: calculator -> web_search -> embeddings_lookup (optional).
    """
    actions: List[Dict[str, Any]] = []
    math = parse_math(prompt)
    if math:
        a, b, op = math
        actions.append({"name": "calculator", "args": {"a": a, "b": b, "operator": op}})

    if wants_search(prompt):
        # If we did math, we'll search for the numeric result; else search the prompt
        # The executor will substitute the previous result automatically if query == "__PREV__"
        query = "__PREV__" if math else prompt
        actions.append({"name": "web_search", "args": {"query": query}})

    if wants_embeddings(prompt):
        q = prompt
        actions.append({"name": "embeddings_lookup", "args": {"query": q}})

    # If none matched, try a gentle fallback: if it's just a number, search it.
    if not actions and re.search(r"\d", prompt):
        actions.append({"name": "web_search", "args": {"query": prompt}})

    # If still nothing, return an empty plan (the agent will produce a default message)
    return actions

def run_offline_agent(prompt: str, verbose: bool = True) -> str:
    """
    Offline 'agent' that:
    - plans which tools to use (no API)
    - runs tools locally
    - chains outputs (calculator result -> web_search query)
    - produces a final, human-friendly message
    """
    if verbose:
        print("-" * 70)
        print("USER:", prompt)
        print("-" * 70)

    plan = plan_actions(prompt)
    if verbose:
        print("PLAN:", plan if plan else "[no tool actions selected]")
        print("-" * 70)

    if not plan:
        return "I didn't find a tool to use for that prompt. Try asking me to calculate or to search."

    last_result: Any = None
    transcript: List[str] = []

    for i, action in enumerate(plan, start=1):
        name = action["name"]
        args = dict(action.get("args", {}))

        # Allow chaining: if query == "__PREV__", feed previous result
        if name == "web_search" and isinstance(args.get("query"), str) and args["query"] == "__PREV__":
            args["query"] = str(last_result) if last_result is not None else ""

        fn = FUNCTION_MAP.get(name)
        if not fn:
            out = f"Error: unknown tool '{name}'"
        else:
            try:
                out = fn(**args)
            except TypeError as te:
                out = f"Error (bad args): {te}"
            except Exception as e:
                out = f"Error: {e}"

        if verbose:
            print(f"STEP {i} → {name}({args})")
            print(f"STEP {i} ← result: {out}")
            print("-" * 70)

        transcript.append(f"{name} => {out}")
        last_result = out

    # Simple final message that summarizes what happened
    summary = " • ".join(transcript)
    return f"Final summary: {summary}"

if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is 12 * 5, then search that number."
    print(run_offline_agent(q, verbose=True))
