# src/core/test_client.py
import time
from openai_client import OpenAIClient

if __name__ == "__main__":
    # 1️⃣ Start timing
    start = time.perf_counter()

    # 2️⃣ Create client (respects DRY_RUN and SIMULATE_RATELIMIT env vars)
    client = OpenAIClient()

    # 3️⃣ Send a small chat prompt
    reply = client.chat([
        {"role": "system", "content": "You are a helpful tutor."},
        {"role": "user", "content": "Explain what a token is in OpenAI in one short sentence."}
    ])

    # 4️⃣ Measure total latency
    latency = time.perf_counter() - start

    # 5️⃣ Print results
    print("\n==========================")
    print(f"AI Reply: {reply.content}")
    print(f"Tokens Used: {reply.total_tokens}")
    print(f"Approx Cost: ${reply.cost_usd:.6f}")
    print(f"Latency: {latency:.2f} s")
    print("==========================\n")
