"""End-to-end tests: launch the REAL app process and exercise every feature.

Run: python scripts/e2e_test.py
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main() -> int:
    port = free_port()
    base = f"http://127.0.0.1:{port}"
    env = dict(os.environ)
    proc = subprocess.Popen(
        [sys.executable, "scripts/run_app.py", "--port", str(port)],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    failures: list[str] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        print(("PASS " if cond else "FAIL ") + name + (f"  {detail}" if detail else ""))
        if not cond:
            failures.append(name)

    def call(method: str, path: str, data: dict | None = None, timeout: int = 120):
        body = json.dumps(data).encode() if data is not None else None
        req = urllib.request.Request(
            base + path,
            data=body,
            headers={"Content-Type": "application/json"} if body else {},
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                try:
                    return resp.status, json.loads(raw.decode())
                except json.JSONDecodeError:
                    return resp.status, raw.decode(errors="ignore")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode(errors="ignore")

    try:
        # wait for startup
        ok = False
        for _ in range(30):
            try:
                st, h = call("GET", "/api/health", timeout=5)
                if st == 200 and h.get("ok"):
                    ok = True
                    break
            except Exception:  # noqa: BLE001
                time.sleep(0.5)
        check("server-start", ok)
        if not ok:
            out = proc.stdout.read() if proc.stdout else ""
            print("SERVER OUTPUT:", out[-2000:])
            return 1

        st, body = call("GET", "/")
        check("index", st == 200 and "<html" in (body or ""), str(st))
        for f in ("app.js", "styles.css"):
            st, body = call("GET", f"/static/{f}")
            check(f"static-{f}", st == 200 and len(body) > 1000)

        st, h = call("GET", "/api/health")
        check("health", h.get("ok") is True and h.get("wiki_pages", 0) > 80)

        st, s = call("GET", "/api/search?q=Booked&raw=1&top=5")
        check("search-en", len(s.get("results", [])) > 0)
        st, s = call("GET", "/api/search?q=" + urllib.parse.quote("OM模块的业务流程"))
        check("search-cjk", len(s.get("results", [])) > 0)

        st, p = call("GET", "/api/pages")
        check("pages", len(p.get("pages", [])) > 80)

        st, pg = call("GET", "/api/page?path=" + urllib.parse.quote("wiki/concepts/order-lifecycle-and-status.md"))
        check("page", "<h1>" in pg.get("html", "") or "Booked" in pg.get("markdown", ""))

        st, raw = call("GET", "/api/raw?path=" + urllib.parse.quote("sources/docs/e48843/chapters/T335476T347163.htm"))
        check("raw-chapter", "Order Header Statuses" in raw.get("text", ""))

        st, g = call("GET", "/api/graph")
        check("graph", len(g.get("nodes", [])) > 50 and len(g.get("links", [])) > 0)

        st, ib = call("GET", "/api/inbox")
        check("inbox", isinstance(ib.get("items"), list))

        st, md = call("POST", "/api/render-md", {"md": "# 标题\n\n- a"})
        check("render-md", "<h1>标题</h1>" in md.get("html", ""))

        st, a = call("POST", "/api/ask", {"question": "订单行何时进入 Awaiting Invoice Interface - On Hold？", "raw": True}, timeout=180)
        check("ask", a.get("mode") in ("llm", "local") and bool(a.get("answer")))

        st, d = call("POST", "/api/ingest?dry_run=1", {"title": "E2E", "content": "x"})
        check("ingest-dry", d.get("dry_run") is True)

        st, real = call("POST", "/api/ingest", {"title": "E2E-SMOKE-请删除", "content": "冒烟"})
        path = ROOT / real.get("path", "")
        check("ingest-real", path.exists())
        if path.exists():
            path.unlink()
        log = ROOT / "wiki" / "log.md"
        lines = log.read_text(encoding="utf-8").splitlines(keepends=True)
        kept, skip = [], False
        for line in lines:
            if line.startswith("## [") and "E2E-SMOKE" in line:
                skip = True
                continue
            if skip:
                if line.startswith("## ["):
                    skip = False
                else:
                    continue
            kept.append(line)
        log.write_text("".join(kept), encoding="utf-8")

        st, _ = call("GET", "/api/not-exist")
        check("404", st == 404)

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()

    print("\n" + (f"{len(failures)} FAILED" if failures else "ALL PASSED"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
