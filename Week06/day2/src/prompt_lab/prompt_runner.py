# -*- coding: utf-8 -*-
"""
Prompt Lab Runner — Week 6 Day 2
- Loads prompts from YAML (supports simple list OR {defaults, tests} schema)
- Builds chat messages (system + few-shot + user)
- Calls OpenAI via shared OpenAIClient
- Logs output, tokens, cost, latency to JSONL per day
- CLI flags: choose file, filter by id/tag, override model/params, dry-run

Run:
  python Day2/src/prompt_lab/prompt_runner.py
  python Day2/src/prompt_lab/prompt_runner.py --file Day2/prompts.yaml --ids concise_summary,creative_story
  python Day2/src/prompt_lab/prompt_runner.py --tags qa --model gpt-4o-mini --temperature 0.3
"""

from __future__ import annotations
import os, sys, time, json, argparse, datetime, logging
from pathlib import Path
from typing import Any, Dict, List

# ---------- Path setup (works when run from Day2 or repo root) ----------
HERE = Path(__file__).resolve()
DAY2_SRC = HERE.parents[1]               # .../Day2/src
WEEK_ROOT = HERE.parents[3]              # .../Week06
WEEK_SRC = WEEK_ROOT / "src"             # .../Week06/src

for p in (DAY2_SRC, WEEK_SRC):
    ps = str(p)
    if ps not in sys.path:
        sys.path.insert(0, ps)

import yaml  # pip install pyyaml
from core.openai_client import OpenAIClient  # Week06/src/core/openai_client.py

# ---------- Logging ----------
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOGGER = logging.getLogger("prompt_runner")

# ---------- Constants ----------
DEFAULT_PROMPTS_FILE = HERE.parents[2] / "prompts.yaml"      # Day2/prompts.yaml
LOG_DIR = HERE.parents[3] / "Day2" / "logs" / "prompts"      # Day2/logs/prompts


# ---------- YAML Loading (supports two schemas) ----------
def _load_yaml(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_tests(path: Path) -> Dict[str, Any]:
    """
    Returns dict: { 'defaults': {...}, 'tests': [ {...}, ... ] }
    Accepts:
      1) Simple list:
        - id: ...
          prompt: ...
      2) Rich schema:
        version: 1
        defaults: {...}
        tests: [ {...}, ... ]
    """
    raw = _load_yaml(path)
    if isinstance(raw, list):
        return {"defaults": {}, "tests": raw}
    if isinstance(raw, dict):
        defaults = raw.get("defaults", {})
        tests = raw.get("tests", [])
        if not isinstance(tests, list):
            raise ValueError("YAML 'tests' must be a list.")
        return {"defaults": defaults, "tests": tests}
    raise ValueError("Unsupported YAML format. Use list or {defaults, tests} dict.")


# ---------- Message Construction ----------
def build_messages(cfg: Dict[str, Any], defaults: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Compose messages with precedence: cfg overrides defaults.
    Supports optional:
      - system: str
      - shots: list of {user: "...", assistant: "..."} pairs for few-shot
      - prompt: final user content
    """
    system_text = cfg.get("system", defaults.get("system", "You are a clear, concise writing assistant."))
    messages = [{"role": "system", "content": system_text}]

    # Few-shot: list of {user, assistant}
    shots = cfg.get("shots", [])
    for ex in shots:
        u = ex.get("user")
        a = ex.get("assistant")
        if not (u and a):
            continue
        messages.append({"role": "user", "content": u})
        messages.append({"role": "assistant", "content": a})

    # Final task prompt
    prompt = cfg.get("prompt")
    if not prompt:
        raise ValueError(f"Test '{cfg.get('id')}' missing 'prompt' field.")
    messages.append({"role": "user", "content": prompt})

    return messages


# ---------- Logging ----------
def save_log(entry: Dict[str, Any]) -> str:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.date.today().isoformat()
    log_path = LOG_DIR / f"{date_str}.jsonl"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return str(log_path)


# ---------- Runner Core ----------
def run_suite(
    file: Path,
    ids: List[str] | None,
    tags: List[str] | None,
    override_model: str | None,
    temperature: float | None,
    top_p: float | None,
    max_tokens: int | None,
    dry_run: bool,
):
    data = load_tests(file)
    defaults = data.get("defaults", {})
    tests: List[Dict[str, Any]] = data.get("tests", [])

    # Filter by ids/tags if provided
    def _match(test: Dict[str, Any]) -> bool:
        if ids:
            if str(test.get("id")) not in ids:
                return False
        if tags:
            ttags = set(test.get("tags", []))
            if not ttags.intersection(tags):
                return False
        return True

    selected = [t for t in tests if _match(t)] if (ids or tags) else tests
    if not selected:
        LOGGER.warning("No tests matched your filters.")
        return

    # Client
    client = OpenAIClient()

    for raw in selected:
        # Merge defaults with test (test overrides)
        cfg = {**defaults, **raw}

        test_id = cfg.get("id", "<no_id>")
        model = override_model or cfg.get("model", "gpt-4o-mini")
        t = temperature if temperature is not None else cfg.get("temperature", 0.7)
        p = top_p if top_p is not None else cfg.get("top_p", 0.9)
        mx = max_tokens if max_tokens is not None else cfg.get("max_tokens", 200)

        # Build messages (system + shots + user)
        try:
            messages = build_messages(cfg, defaults)
        except Exception as e:
            LOGGER.error(f"[{test_id}] Message build failed: {e}")
            save_log({
                "id": test_id, "status": "build_error", "error": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            })
            continue

        # Dry-run prints the composed config/messages without calling API
        if dry_run:
            print(json.dumps({
                "id": test_id, "model": model, "temperature": t, "top_p": p, "max_tokens": mx,
                "messages": messages
            }, ensure_ascii=False, indent=2))
            continue

        # Call model
        start = time.perf_counter()
        try:
            output = client.chat(
                messages=messages,
                model=model,
                temperature=t,
                top_p=p,
                max_tokens=mx,
            )
            latency = round(time.perf_counter() - start, 3)
            usage = client.last_usage
            cost = client.last_cost
            token_detail = client.last_token_counts or {}

            entry = {
                "id": test_id,
                "status": "ok",
                "model": model,
                "temperature": t,
                "top_p": p,
                "max_tokens": mx,
                "latency_s": latency,
                "timestamp": datetime.datetime.now().isoformat(),
                "tokens": usage,
                "token_detail": token_detail,
                "cost_usd": cost,
                "output": output,
                "tags": cfg.get("tags", []),
            }
            path = save_log(entry)
            LOGGER.info(f"[{test_id}] logged -> {path} (lat={latency}s, tokens={usage}, cost={cost})")

        except Exception as e:
            latency = round(time.perf_counter() - start, 3)
            entry = {
                "id": test_id,
                "status": "api_error",
                "model": model,
                "temperature": t,
                "top_p": p,
                "max_tokens": mx,
                "latency_s": latency,
                "timestamp": datetime.datetime.now().isoformat(),
                "error": str(e),
            }
            path = save_log(entry)
            LOGGER.error(f"[{test_id}] ERROR -> {e} (logged {path})")


# ---------- CLI ----------
def parse_args():
    ap = argparse.ArgumentParser(description="Run prompt tests from YAML and log results.")
    ap.add_argument("--file", default=str(DEFAULT_PROMPTS_FILE), help="Path to prompts.yaml")
    ap.add_argument("--ids", default="", help="Comma-separated test IDs to run")
    ap.add_argument("--tags", default="", help="Comma-separated tags to filter tests")
    ap.add_argument("--model", dest="model", default=None, help="Override model for all tests")
    ap.add_argument("--temperature", type=float, default=None, help="Override temperature")
    ap.add_argument("--top_p", type=float, default=None, help="Override top_p")
    ap.add_argument("--max_tokens", type=int, default=None, help="Override max_tokens")
    ap.add_argument("--dry-run", action="store_true", help="Print messages/config without calling the API")
    return ap.parse_args()

def main():
    args = parse_args()
    file = Path(args.file)

    ids = [s for s in args.ids.split(",") if s.strip()] or None
    tags = [s for s in args.tags.split(",") if s.strip()] or None

    run_suite(
        file=file,
        ids=ids,
        tags=tags,
        override_model=args.model,
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
        dry_run=args.dry_run,
    )

if __name__ == "__main__":
    main()
