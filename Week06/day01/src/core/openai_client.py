# src/core/openai_client.py

import os
import time
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional

from dotenv import load_dotenv

# ---- OpenAI SDK imports (tolerant if not installed in DRY mode) --------------
try:
    from openai import OpenAI
    from openai import APIError, RateLimitError, APIConnectionError, AuthenticationError
    from openai._exceptions import APITimeoutError  # correct timeout class in latest SDK
except Exception:  # pragma: no cover
    OpenAI = None
    APIError = RateLimitError = APIConnectionError = AuthenticationError = APITimeoutError = Exception  # type: ignore

# ---- Local simulated exception for demoing retries ---------------------------
class SimulatedRateLimit(Exception):
    """Used to fake 429s for retry/backoff demos without making network calls."""
    pass

# ---- Env + logging -----------------------------------------------------------
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

API_KEY = os.getenv("OPENAI_API_KEY", "")
DRY_RUN = os.getenv("DRY_RUN", "0") == "1"                 # set to 1 to avoid network/spend
SIMULATE_RATELIMIT = os.getenv("SIMULATE_RATELIMIT", "0") == "1"  # set to 1 to force retries

# ---- Pricing table (USD per 1K tokens) ---------------------------------------
PRICING_USD_PER_1K = {
    "gpt-4o":       {"in": 0.005,   "out": 0.015},
    "gpt-4o-mini":  {"in": 0.00015, "out": 0.00060},
    # fallback if an unknown model is used
    "_default":     {"in": 0.00020, "out": 0.00080},
}

@dataclass
class ChatResult:
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    latency_s: float
    model: str

class OpenAIClient:
    """
    Friendly wrapper:
    - DRY_RUN mode for zero-cost practicing
    - Exponential backoff (1s, 2s, 4s ...)
    - Clean error messages
    - Token + cost logging per call
    """

    def __init__(self, api_key: Optional[str] = None, default_model: str = "gpt-4o-mini"):
        self.api_key = api_key or API_KEY
        self.model_default = default_model

        if DRY_RUN:
            logging.info("DRY_RUN=1 → No network calls will be made. Returning mock responses.")
            self.client = None
        else:
            if not self.api_key:
                logging.warning("No OPENAI_API_KEY found. Set it in .env or enable DRY_RUN=1.")
            self.client = OpenAI(api_key=self.api_key) if OpenAI else None

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 300,
        temperature: float = 0.2,
        retries: int = 3,
        timeout: int = 20,
    ) -> ChatResult:
        """Send a chat completion with retries + cost logging. Returns ChatResult."""
        model = model or self.model_default
        start = time.perf_counter()

        # ---- DRY mode (no network, no spend) ---------------------------------
        if DRY_RUN:
            time.sleep(0.05)
            content = "[DRY_RUN] Hello! (no API call made)"
            prompt_tokens, completion_tokens = 30, 15  # pretend usage
            total = prompt_tokens + completion_tokens
            cost = self._calc_cost(model, prompt_tokens, completion_tokens)
            latency = time.perf_counter() - start
            self._log_cost(model, total, prompt_tokens, completion_tokens, cost, latency)
            return ChatResult(content, prompt_tokens, completion_tokens, total, cost, latency, model)

        # ---- Real call path with optional simulation of rate limits ----------
        def _do_call():
            if SIMULATE_RATELIMIT:
                logging.warning("⚠️ Simulating a RateLimitError for retry demo...")
                raise SimulatedRateLimit("Simulated 429: Too Many Requests")

            return self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout,
            )

        response = self._retry(_do_call, retries=retries)

        latency = time.perf_counter() - start

        usage = getattr(response, "usage", None)
        prompt_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
        completion_tokens = getattr(usage, "completion_tokens", 0) if usage else 0
        total = getattr(usage, "total_tokens", prompt_tokens + completion_tokens)

        content = response.choices[0].message.content if response and response.choices else ""
        cost = self._calc_cost(model, prompt_tokens, completion_tokens)

        self._log_cost(model, total, prompt_tokens, completion_tokens, cost, latency)

        return ChatResult(content, prompt_tokens, completion_tokens, total, cost, latency, model)

    # ------------------------- helpers -----------------------------------------
    def _retry(self, func, retries: int = 3, base_delay: float = 1.0):
        """Exponential backoff: 1s, 2s, 4s ..."""
        for attempt in range(retries):
            try:
                return func()
            except (RateLimitError, APITimeoutError, APIConnectionError, SimulatedRateLimit) as e:
                wait = base_delay * (2 ** attempt)
                logging.warning(f"Retry {attempt+1}/{retries} after transient error: {e}. Waiting {wait:.1f}s.")
                time.sleep(wait)
            except AuthenticationError as e:
                raise RuntimeError(
                    "Authentication failed. Check your OPENAI_API_KEY in .env "
                    "or run with DRY_RUN=1 to practice without a key."
                ) from e
            except APIError as e:
                wait = base_delay * (2 ** attempt)
                logging.warning(f"APIError on attempt {attempt+1}: {e}. Waiting {wait:.1f}s.")
                time.sleep(wait)
            except Exception as e:
                raise RuntimeError(f"Unexpected error while calling OpenAI API: {e}") from e

        raise RuntimeError("Max retries reached without success.")

    def _calc_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        prices = PRICING_USD_PER_1K.get(model, PRICING_USD_PER_1K["_default"])
        cost_in = (prompt_tokens / 1000.0) * prices["in"]
        cost_out = (completion_tokens / 1000.0) * prices["out"]
        return round(cost_in + cost_out, 8)

    def _log_cost(
        self,
        model: str,
        total: int,
        prompt_tokens: int,
        completion_tokens: int,
        cost: float,
        latency: float,
    ):
        logging.info(
            f"Model={model} | prompt={prompt_tokens} | completion={completion_tokens} | "
            f"total={total} | cost=${cost:.6f} | latency={latency:.2f}s"
        )
