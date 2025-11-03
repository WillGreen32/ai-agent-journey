import os, time, logging
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Adjust pricing if your account shows different rates.
# Prices are USD per 1K tokens (input/output).
PRICING = {
    "gpt-4o":       {"in": 0.005,   "out": 0.015},
    "gpt-4o-mini":  {"in": 0.00015, "out": 0.00060},
}

class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set in environment/.env")
        self.client = OpenAI(api_key=api_key)
        self.timeout = timeout

        # last-call metadata
        self.last_usage: Optional[int] = None
        self.last_cost: Optional[float] = None
        self.last_token_counts: Optional[Dict[str, int]] = None

    def _calc_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        price = PRICING.get(model, PRICING["gpt-4o-mini"])
        inp = (prompt_tokens / 1000.0) * price["in"]
        out = (completion_tokens / 1000.0) * price["out"]
        return inp + out

    def _retry(self, func, *args, retries=3, delay=1, **kwargs):
        for i in range(retries):
            try:
                return func(*args, **kwargs)
            except OpenAIError as e:
                logging.warning(f"[OpenAI] Attempt {i+1}/{retries} failed: {e}")
                time.sleep(delay * (2 ** i))
        raise

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 300,
    ) -> str:
        """Send a chat completion request. Returns assistant text.
        Side effects: sets last_usage, last_cost, last_token_counts.
        """
        start = time.perf_counter()
        resp = self._retry(
            self.client.chat.completions.create,
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            timeout=self.timeout,
        )
        latency = time.perf_counter() - start

        # Usage
        prompt_tokens = getattr(resp.usage, "prompt_tokens", None) or 0
        completion_tokens = getattr(resp.usage, "completion_tokens", None) or 0
        total_tokens = getattr(resp.usage, "total_tokens", None) or (prompt_tokens + completion_tokens)

        cost = self._calc_cost(model, prompt_tokens, completion_tokens)

        self.last_usage = total_tokens
        self.last_cost = cost
        self.last_token_counts = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        }

        logging.info(
            f"Model={model} | temp={temperature} top_p={top_p} max_tokens={max_tokens} | "
            f"tokens: in={prompt_tokens} out={completion_tokens} total={total_tokens} | "
            f"cost=${cost:.6f} | latency={latency:.2f}s"
        )

        return resp.choices[0].message.content
