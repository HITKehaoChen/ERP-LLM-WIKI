"""Optional OpenAI-compatible chat client for the Q&A endpoint."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_BASE = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
CONFIG_PATH = Path(__file__).resolve().parent / "llm_config.json"


def _config() -> dict:
    """Merge optional local config file with environment overrides.

    Local file: app/llm_config.json  (gitignored, keeps API keys out of git)
      {"base_url": "...", "api_key": "...", "model": "..."}
    Env overrides: OPENAI_API_KEY / OPENAI_BASE_URL / OPENAI_MODEL
    """
    cfg: dict = {}
    if CONFIG_PATH.exists():
        try:
            cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            cfg = {}
    return {
        "api_key": os.environ.get("OPENAI_API_KEY", "").strip() or str(cfg.get("api_key", "")).strip(),
        "base_url": os.environ.get("OPENAI_BASE_URL", "").strip()
        or str(cfg.get("base_url", "")).strip()
        or DEFAULT_BASE,
        "model": os.environ.get("OPENAI_MODEL", "").strip()
        or str(cfg.get("model", "")).strip()
        or DEFAULT_MODEL,
    }


def configured() -> bool:
    return bool(_config()["api_key"])


def ask(system: str, user: str, timeout: int = 90) -> str | None:
    """Call an OpenAI-compatible /chat/completions endpoint. Returns None on
    any failure so the caller can degrade to local retrieval answers."""
    cfg = _config()
    key = cfg["api_key"]
    if not key:
        return None
    base = cfg["base_url"].rstrip("/")
    model = cfg["model"]
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
