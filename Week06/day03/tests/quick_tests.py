# tests/quick_tests.py
from pathlib import Path
import sys

# Ensure we can import from src/
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from utils.token_tools import count_tokens, estimate_cost, chunk_text_by_tokens

print("== Token count test ==")
print("Tokens:", count_tokens("gpt-4o", "OpenAI models are powerful!"))

print("\n== Cost estimate test ==")
print("Cost (gpt-4o-mini, 1000 in, 300 out): $", estimate_cost("gpt-4o-mini", 1000, 300))

print("\n== Chunking test ==")
text = ("Artificial intelligence is transforming industries worldwide. From healthcare to finance, "
        "automation makes tasks faster and more accurate. However, large language models have limits. "
        "One helpful technique is chunking; it splits long text into smaller sections so each part fits "
        "within the model's memory window. This keeps requests reliable and reduces cost.")
chunks = chunk_text_by_tokens(text, max_tokens=60, model="gpt-4o-mini")
for i, c in enumerate(chunks, 1):
    print(f"Chunk {i} ({count_tokens('gpt-4o-mini', c)} tokens): {c}")
