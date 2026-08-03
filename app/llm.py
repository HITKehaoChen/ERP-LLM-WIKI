"""Optional OpenAI-compatible chat client for the Q&A endpoint."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

DEFAULT_BASE = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"


def configured() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY", "").strip())


def ask(system: str, user: str, timeout: int = 90) -> str | None:
    """Call an OpenAI-compatible /chat/completions endpoint. Returns None on
    any failure so the caller can degrade to local retrieval answers."""
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    base = os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE).rstrip("/")
    model = os.environ.get("OPENAI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    url = f"{base}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]
    except (urllib.error.URLError, KeyError, IndexError, ValueError, OSError) as exc:
        print(f"[llm] request failed: {exc}")
        return None
