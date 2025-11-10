# src/agents/manual_agent.py
"""
Year-6 explanation:
This agent looks up relevant memories, puts them above your question,
asks the model, then saves the new exchange back to memory.
"""

from typing import List, Callable
from memory.vector_memory import (
    init_db,
    get_relevant_memories,
    add_memory,
    _toy_embed,   # placeholder embedding; swap later
)

# ---------------- Model stub (replace later) ----------------

def fake_model_reply(prompt: str) -> str:
    """
    Very small placeholder that echoes the prompt.
    Replace with a real OpenAI call when ready.
    """
    return (
        "Thanks! I used the context above to answer.\n"
        "(This is a stubbed reply. Swap me with a real model call.)"
    )

# ---------------- Agent ----------------

class ManualAgent:
    def __init__(self, embeddings_lookup: Callable[[str], List[float]] = _toy_embed, top_k: int = 3):
        """
        embeddings_lookup: function that turns text -> list[float] (the embedding)
        top_k: how many memories to inject each time
        """
        init_db()
        self.embeddings_lookup = embeddings_lookup
        self.top_k = top_k

    def run(self, user_query: str, remember_response: bool = True) -> str:
        # ---- retrieve relevant memories before model call ----
        relevant = get_relevant_memories(user_query, self.embeddings_lookup, top_k=self.top_k)
        context = "\n".join(relevant) if relevant else "(none)"

        # ---- build the final prompt sent to the model ----
        prompt = f"Relevant context:\n{context}\n\nUser: {user_query}"

        # ---- call the model (stub for now) ----
        agent_response = fake_model_reply(prompt)

        # ---- save the new interaction back into memory ----
        if remember_response:
            add_memory(f"{user_query} → {agent_response}", self.embeddings_lookup)

        # (Optional) return a developer-friendly view so you can see injection working
        return f"🧠 Context used:\n{context}\n\n💬 Answer:\n{agent_response}"

# ---------------- Quick manual test ----------------

if __name__ == "__main__":
    agent = ManualAgent(embeddings_lookup=_toy_embed, top_k=3)

    # Seed a fact we want the agent to recall later
    add_memory("User said their favorite color is blue.", agent.embeddings_lookup)

    # Should recall the 'blue' memory
    print(agent.run("What color do I like?"))
