# src/agent_preview/basic_agent.py
from src.utils.cost_tracker import track_cost

# ==========================
# 🧰 TOOLS
# ==========================

def calculator(a, b, op="+"):
    """Basic calculator supporting +, -, *, /."""
    if op == "+": return a + b
    if op == "-": return a - b
    if op == "*": return a * b
    if op == "/": return a / b
    raise ValueError("Unsupported operation")

def text_analyzer(text):
    """Return simple text stats."""
    return {"word_count": len(text.split()), "char_count": len(text)}

# ==========================
# ⚙️ SAFE CALL WRAPPER
# ==========================

def safe_call(tool_name, fn, *args, **kwargs):
    """Safely call a tool, catching errors instead of crashing."""
    try:
        return fn(*args, **kwargs), None
    except Exception as e:
        return None, f"{tool_name} failed: {e}"

# ==========================
# 🔁 AGENT LOOP
# ==========================

def agent_loop(task: str, max_steps: int = 2):
    """Simple agent loop with reasoning, tool use, repeat, and cost tracking."""
    state = {"task": task, "step": 0, "last_tool": None, "last_result": None}

    print(f"\n🧠 Task: {task}")

    while state["step"] < max_steps:
        state["step"] += 1
        print(f"\n— Step {state['step']} —")

        # 1️⃣ Reason
        reasoning = "If task has numbers → use calculator, else → text analyzer."
        print("Reasoning:", reasoning)

        # 2️⃣ Act (safe)
        if any(ch.isdigit() for ch in task):
            tool = "calculator"
            result, err = safe_call("calculator", calculator, 5, 3, "+")
        else:
            tool = "text_analyzer"
            result, err = safe_call("text_analyzer", text_analyzer, task)

        if err:
            print("⚠️", err)
            track_cost("gpt-4o-mini", 50, {"tool": tool, "error": True})
            return {"tool": tool, "error": err}

        # 3️⃣ Evaluate
        print(f"Used {tool} → Result:", result)
        state.update({"last_tool": tool, "last_result": result})
        track_cost("gpt-4o-mini", 100, {"tool": tool, "step": state["step"]})

        # 🔁 demo repeat
        if tool == "text_analyzer" and state["step"] == 1:
            print("🔁 Not done yet — doing a second pass just to demo repeat.")
            continue

        print("✅ Step complete — stopping loop.\n")
        break

    return {"tool": state["last_tool"], "result": state["last_result"]}

# ==========================
# ▶️ DRIVER (CLI ARG)
# ==========================

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
        agent_loop(task)
    else:
        agent_loop("Analyze this sentence for word count.")
        agent_loop("What is 5 + 3?")
