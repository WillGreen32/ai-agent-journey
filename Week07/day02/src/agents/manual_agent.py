# src/agents/manual_agent.py
# Manual multi-tool agent loop with an OFFLINE mock client (no API spend).
# Flip USE_REAL_API=True later to use the real OpenAI client.

import json, time, re
from typing import List, Dict, Any

# ──────────────────────────────────────────────────────────────────────────────
# Imports: our local tools
from functions import calculator, web_search, embeddings_lookup

# Tool registry (maps model tool name -> Python function)
TOOLS = {
    "calculator": calculator.run,
    "web_search": web_search.run,
    "embeddings_lookup": embeddings_lookup.run,
}

# Tool schemas (tell model what the tools are and what inputs they take)
TOOL_SCHEMAS = [
    calculator.schema,
    web_search.schema,
    embeddings_lookup.schema,
]

# ──────────────────────────────────────────────────────────────────────────────
# Toggle: use real OpenAI API or the offline mock
USE_REAL_API = False

if USE_REAL_API:
    # Real client (will require `pip install openai` and an API key)
    from openai import OpenAI
    client = OpenAI()
else:
    # ----------------- Mock classes that mimic OpenAI responses ----------------
    class _MockToolCallFn:
        def __init__(self, name: str, arguments: str):
            self.name = name
            self.arguments = arguments

    class _MockToolCall:
        def __init__(self, name: str, arguments: Dict[str, Any]):
            self.function = _MockToolCallFn(name, json.dumps(arguments))

    class _MockMsg:
        def __init__(self, content=None, tool_calls: List[_MockToolCall] = None):
            self.content = content
            self.tool_calls = tool_calls or []

    class _MockChoice:
        def __init__(self, message: _MockMsg):
            self.message = message

    class _MockUsage:
        # Fake token counts just to exercise logging
        def __init__(self, total_tokens: int):
            self.total_tokens = total_tokens

    class _MockResponse:
        def __init__(self, message: _MockMsg, tokens: int = 120):
            self.choices = [_MockChoice(message)]
            self.usage = _MockUsage(tokens)

    class _MockChatCompletions:
        """
        This mock "decides" which tool to call by peeking at conversation text:
          • If multiplication like "5 * 12" appears and calc result not yet present → call calculator
          • If population of Japan requested and not yet fetched → call web_search
          • Else, produce a final message combining known results.
        """
        def create(self, model: str, messages: List[Dict[str, str]], tools: List[dict]):
            # Helper: get latest user request and current tool outputs
            full_text = " ".join(m.get("content", "") for m in messages)
            last_user = ""
            for m in reversed(messages):
                if m.get("role") == "user":
                    last_user = m.get("content", "")
                    break

            # Collect tool results seen so far
            tool_texts = [m["content"] for m in messages if m.get("role") == "tool"]
            have_calc = any(re.search(r"\b\d+\b", t) for t in tool_texts)
            have_jp_pop = any("125,000,000" in t or "Approximately 125,000,000" in t for t in tool_texts)

            # Detect desire for multiplication like "5 * 12" or "5x12" or "5 × 12"
            mult_match = re.search(r"(\d+)\s*[\*x×]\s*(\d+)", last_user)
            need_calc = bool(mult_match) and not have_calc

            # Detect desire for Japan population
            need_jp_pop = ("population of japan" in last_user.lower()) and not have_jp_pop

            # If we still need to compute multiplication → tool call: calculator
            if need_calc:
                a = float(mult_match.group(1))
                b = float(mult_match.group(2))
                tool_call = _MockToolCall("calculator", {"a": a, "b": b, "op": "*"})
                return _MockResponse(_MockMsg(tool_calls=[tool_call]), tokens=80)

            # If we need Japan population → tool call: web_search
            if need_jp_pop:
                tool_call = _MockToolCall("web_search", {"query": "population of japan"})
                return _MockResponse(_MockMsg(tool_calls=[tool_call]), tokens=90)

            # Otherwise, produce a final message using whatever tool results exist.
            # Try to find a simple number from calculator and a JP population in tool_texts.
            calc_num = None
            for t in tool_texts:
                m = re.search(r"\b\d+(\.\d+)?\b", t)
                if m:
                    calc_num = m.group(0)
                    break
            jp_pop = None
            for t in tool_texts:
                if "125,000,000" in t:
                    jp_pop = "125,000,000"
                elif "Approximately 125,000,000" in t:
                    jp_pop = "125,000,000"

            # Compose final answer text
            if calc_num and jp_pop:
                text = (
                    f"Multiplication result = {calc_num}. "
                    f"Japan population ≈ {jp_pop}. "
                    f"Combined reasoning done."
                )
            elif calc_num:
                text = f"Computed result = {calc_num}. (No population fetched yet.)"
            elif jp_pop:
                text = f"Japan population ≈ {jp_pop}. (No calculation found.)"
            else:
                text = "I have no pending tool actions. Provide a new query."

            return _MockResponse(_MockMsg(content=text), tokens=60)

    class _MockChat:
        def __init__(self):
            self.completions = _MockChatCompletions()

    class _MockClient:
        def __init__(self):
            self.chat = _MockChat()

    client = _MockClient()
# ──────────────────────────────────────────────────────────────────────────────


def manual_agent(query: str):
    """Manual agent loop with simple inline logging (iteration, tokens, latency, tool)."""
    conversation = [{"role": "user", "content": query}]
    total_tokens = 0
    t0 = time.time()
    iteration = 0

    while True:
        iteration += 1

        # ── start timing this iteration
        iter_start = time.time()

        # model "decides"
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation,
            tools=TOOL_SCHEMAS
        )

        # tokens (mock usage when offline)
        iter_tokens = getattr(getattr(response, "usage", None), "total_tokens", 0)
        total_tokens += iter_tokens

        msg = response.choices[0].message

        # ── end timing (decision latency for this iteration)
        decision_latency = time.time() - iter_start

        # If model requested tool(s), run them and log each tool execution
        if getattr(msg, "tool_calls", None):
            for call in msg.tool_calls:
                name = call.function.name
                args = json.loads(call.function.arguments)

                # run tool and time it
                tool_start = time.time()
                try:
                    result = TOOLS[name](**args)
                    tool_error = None
                except Exception as e:
                    result = None
                    tool_error = str(e)

                tool_latency = time.time() - tool_start

                # append tool result so model can "see" it next loop
                conversation.append({"role": "tool", "content": str(result)})

                # ── inline LOGS
                print(
                    f"Iteration {iteration} | Tool: {name} | "
                    f"Tokens: {iter_tokens} | "
                    f"DecisionLatency: {decision_latency:.2f}s | "
                    f"ToolLatency: {tool_latency:.2f}s | "
                    f"Error: {tool_error or 'None'}"
                )

            # continue looping (model will read tool outputs next turn)
            continue

        # No tool calls → final answer
        print("\n🧠 Final Answer:", msg.content)
        break

    total_latency = time.time() - t0
    print(f"\nRun Summary → TotalTokens: {total_tokens} | TotalTime: {total_latency:.2f}s")



# Convenience: quick test from CLI
if __name__ == "__main__":
    # Example from your spec:
    manual_agent("What is 5 * 12 plus the population of Japan?")
