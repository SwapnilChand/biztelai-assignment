"""Two interchangeable LLM backends behind one function.

- ollama: a small model running on the laptop (default granite4.2:3b). Nothing
  leaves the machine, which is what a plant would want, but it is slow on a CPU.
- groq: a hosted open-weight model (default openai/gpt-oss-120b). Fast, free
  tier, but the question and the retrieved text go to an external API.

Pick with LLM_PROVIDER=ollama|groq. Both are asked for the same JSON shape.
"""

from __future__ import annotations

import json
import os
import time

import httpx

PROVIDER = os.getenv("LLM_PROVIDER", "groq" if os.getenv("GROQ_API_KEY") else "ollama")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "granite4.2:3b")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
# The free tier has a daily token cap per model (200k for gpt-oss-120b, about 40
# questions). When it runs out, switch to a smaller model with its own cap
# instead of telling a supervisor "try again tomorrow".
GROQ_FALLBACK_MODEL = os.getenv("GROQ_FALLBACK_MODEL", "openai/gpt-oss-20b")

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "found": {"type": "boolean"},
        "answer": {"type": "string"},
        "sources": {"type": "array", "items": {"type": "string"}},
        "revision_note": {"type": "string"},
    },
    "required": ["found", "answer", "sources", "revision_note"],
}

REVISION_SCHEMA = {
    "type": "object",
    "properties": {"changed": {"type": "boolean"}, "note": {"type": "string"}},
    "required": ["changed", "note"],
}

_exhausted: dict[str, float] = {}  # groq model -> time its daily cap frees up


def model_name(provider: str | None = None) -> str:
    provider = provider or PROVIDER
    if provider == "ollama":
        return f"ollama/{OLLAMA_MODEL}"
    return f"groq/{_groq_model()}"


def _groq_model() -> str:
    return GROQ_FALLBACK_MODEL if _exhausted.get(GROQ_MODEL, 0) > time.time() else GROQ_MODEL


def _groq(system: str, user: str) -> tuple[str, str]:
    for attempt in range(6):
        model = _groq_model()
        r = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
            json={
                "model": model,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                "response_format": {"type": "json_object"},
                "temperature": 0,
                "reasoning_effort": "low",
            },
            timeout=60,
        )
        if r.status_code != 429 or attempt == 5:
            break
        wait = float(r.headers.get("retry-after", 5))
        if wait > 30 and model == GROQ_MODEL:
            # daily cap, not the per-minute one: fall back for that long
            _exhausted[GROQ_MODEL] = time.time() + wait
            continue
        # per-minute cap (8k tokens, about 3 questions): wait for the window
        time.sleep(min(wait, 30) + 0.5)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"], f"groq/{model}"


def _ollama(system: str, user: str, schema: dict) -> tuple[str, str]:
    r = httpx.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": OLLAMA_MODEL,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "format": schema,
            "think": False,
            "stream": False,
            "options": {"temperature": 0, "num_ctx": 8192},
        },
        timeout=300,
    )
    r.raise_for_status()
    return r.json()["message"]["content"], f"ollama/{OLLAMA_MODEL}"


def complete_json(system: str, user: str, provider: str | None = None,
                  schema: dict = ANSWER_SCHEMA) -> dict:
    """Ask for JSON; the model that actually answered is returned under "_model"."""
    provider = provider or PROVIDER
    content, model = _ollama(system, user, schema) if provider == "ollama" else _groq(system, user)
    out = json.loads(content)
    out["_model"] = model
    return out
