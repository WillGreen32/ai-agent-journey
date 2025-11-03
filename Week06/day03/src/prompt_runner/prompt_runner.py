# week_6/day_3/src/prompt_runner/prompt_runner.py
"""
Prompt Runner (Pre-Flight)
- Loads a prompt text file
- Counts tokens for a given model
- Estimates cost (optionally include expected completion tokens)
- Warns if cost/size exceed thresholds
- Optionally chunks the text and logs results

No API key needed. Purely local checks.
"""

from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from datetime import datetime

# Allow imports like: from utils.token_tools import ...
import sys
ROOT = Path(__file__).resolve().parents[2]  # .../day_3/
sys.path.append(str(ROOT / "src"))

from utils.token_tools import (
    count_tokens,
    estimate_cost,
    estimate_cost_for_text,
    chunk_text_by_tokens,
)

# ----------------------------
# Helpers
# ----------------------------

def load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")

    for enc in ("utf-8", "utf-8-sig", "utf-16", "utf-16-le", "utf-16-be", "cp1252"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("utf-8", b"", 0, 1, f"Could not decode {path}. Re-save as UTF-8.")


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def save_log(payload: dict, logs_dir: Path):
    ensure_dir(logs_dir)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out = logs_dir / f"{stamp}.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out

# ----------------------------
# Main
# ----------------------------

def main():
    parser = argparse.ArgumentParser(description="Pre-flight prompt estimator (no API)")
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="Model name for token counting/pricing (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "--path",
        default=str(ROOT / "data" / "sample_texts" / "demo_text.txt"),
        help="Path to a .txt file containing your prompt text",
    )
    parser.add_argument(
        "--expected-completion",
        type=int,
        default=200,
        help="Estimated number of output tokens you expect the model to return",
    )
    parser.add_argument(
        "--warn-cost",
        type=float,
        default=0.02,
        help="Warn if predicted cost exceeds this USD value (default: $0.02)",
    )
    parser.add_argument(
        "--warn-tokens",
        type=int,
        default=6000,
        help="Warn if prompt tokens exceed this amount (rough safety budget)",
    )
    parser.add_argument(
        "--chunk",
        action="store_true",
        help="Also chunk the prompt and show per-chunk token counts",
    )
    parser.add_argument(
        "--max-chunk-tokens",
        type=int,
        default=300,
        help="Max tokens per chunk when --chunk is used (default: 300)",
    )
    args = parser.parse_args()

    prompt_path = Path(args.path)
    model = args.model

    # 1) Load prompt text
    prompt_text = load_text(prompt_path)

    # 2) Count tokens & estimate cost
    prompt_tokens = count_tokens(model, prompt_text)
    est_cost = estimate_cost(model, prompt_tokens, args.expected_completion)

    # 3) Print summary
    print("\n=== PRE-FLIGHT ESTIMATE ===")
    print(f"Model: {model}")
    print(f"Prompt file: {prompt_path}")
    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Expected completion tokens: {args.expected_completion}")
    print(f"Estimated cost (USD): ${est_cost:.6f}")

    # 4) Warnings
    if prompt_tokens > args.warn_tokens:
        print(f"⚠️  Warning: Prompt is large (> {args.warn_tokens} tokens). Consider summarizing or chunking.")
    if est_cost > args.warn_cost:
        print(f"⚠️  Warning: This prompt may cost more than ${args.warn_cost:.2f} (predicted: ${est_cost:.4f}).")

    # 5) Optional chunking
    chunks_info = None
    if args.chunk:
        chunks = chunk_text_by_tokens(prompt_text, args.max_chunk_tokens, model=model)
        print("\n=== CHUNKING ===")
        print(f"Max tokens per chunk: {args.max_chunk_tokens}")
        print(f"Total chunks: {len(chunks)}")
        chunks_info = []
        for i, c in enumerate(chunks, 1):
            ct = count_tokens(model, c)
            print(f"- Chunk {i}: {ct} tokens")
            chunks_info.append({"index": i, "tokens": ct})

    # 6) Log to /logs/cost_tests/
    logs_dir = ROOT / "logs" / "cost_tests"
    payload = {
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "prompt_file": str(prompt_path),
        "prompt_tokens": prompt_tokens,
        "expected_completion_tokens": args.expected_completion,
        "estimated_cost_usd": est_cost,
        "warn_cost_threshold": args.warn_cost,
        "warn_tokens_threshold": args.warn_tokens,
        "chunking_used": bool(args.chunk),
        "max_chunk_tokens": args.max_chunk_tokens if args.chunk else None,
        "chunks_summary": chunks_info,
    }
    out_file = save_log(payload, logs_dir)
    print(f"\n📝 Logged pre-flight details to: {out_file}\n")

if __name__ == "__main__":
    main()
