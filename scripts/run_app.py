"""Start the local LLM Wiki web UI.

Usage:
  python scripts/run_app.py                # http://127.0.0.1:8000
  python scripts/run_app.py --port 9000

Optional env: OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"
sys.path.insert(0, str(APP))

import server  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    server.main_serve(args.host, args.port)


if __name__ == "__main__":
    main()
