"""Smoke tests for the local LLM Wiki web UI (stdlib only)."""

from __future__ import annotations

import json
import sys
import threading
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"
sys.path.insert(0, str(APP))

import server  # noqa: E402

BASE = ""


def call(method: str, path: str, data: dict | None = None) -> dict:
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(
        BASE + path,
        data=body,
        headers={"Content-Type": "application/json"} if body else {},
        method=method,
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    httpd = server.ThreadedApp(("127.0.0.1", 0), server.Handler)
    port = httpd.server_address[1]
    global BASE
    BASE = f"http://127.0.0.1:{port}"
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()

    failures: list[str] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        print(("PASS " if cond else "FAIL ") + name + (f"  {detail}" if detail else ""))
        if not cond:
            failures.append(name)

    try:
        h = call("GET", "/api/health")
        check("health", h.get("ok") is True and h.get("wiki_pages", 0) > 0, str(h))

        s = call("GET", "/api/search?q=Booked&raw=1&top=5")
        check("search", len(s.get("results", [])) > 0, f"{len(s.get('results', []))} hits")

        p = call("GET", "/api/page?path=" + urllib.parse.quote("wiki/concepts/order-lifecycle-and-status.md"))
        check("page", "Booked" in p.get("markdown", "") and "<table>" in p.get("html", ""))

        a = call("POST", "/api/ask", {"question": "订单行什么时候进入 Awaiting Invoice Interface - On Hold？", "raw": True})
        check("ask-local", a.get("mode") == "local" and a.get("answer"), a.get("mode", ""))

        d = call("POST", "/api/ingest?dry_run=1", {"title": "测试", "content": "内容", "source_url": "http://x"})
        check("ingest-dryrun", d.get("dry_run") is True and d.get("path", "").endswith(".md"))

        real = call(
            "POST",
            "/api/ingest",
            {"title": "SMOKE-TEST-请删除", "content": "冒烟测试内容", "source_url": ""},
        )
        path = ROOT / real.get("path", "")
        check("ingest-real", path.exists() and real.get("dry_run") is False, real.get("path", ""))
        if path.exists():
            path.unlink()
        # remove the log lines added by the smoke test
        log = ROOT / "wiki" / "log.md"
        lines = log.read_text(encoding="utf-8").splitlines(keepends=True)
        kept, skip = [], False
        for line in lines:
            if line.startswith("## [") and "SMOKE-TEST" in line:
                skip = True
                continue
            if skip:
                if line.startswith("## ["):
                    skip = False
                else:
                    continue
            kept.append(line)
        log.write_text("".join(kept), encoding="utf-8")

        r = call("POST", "/api/render-md", {"md": "# 标题\n\n- a\n- b"})
        check("render-md", "<h1>标题</h1>" in r.get("html", "") and "<li>a</li>" in r.get("html", ""))

        ib = call("GET", "/api/inbox")
        check("inbox-list", isinstance(ib.get("items"), list))

    finally:
        httpd.shutdown()

    print("\n" + (f"{len(failures)} FAILED" if failures else "ALL PASSED"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
