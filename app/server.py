"""Zero-dependency local web UI for the Oracle EBS LLM Wiki.

Run:
  python app/server.py --port 8000

Optional env:
  OPENAI_API_KEY / OPENAI_BASE_URL / OPENAI_MODEL  -> enable LLM answers
  (without a key the /api/ask endpoint returns retrieval-based answers)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent

import sys as _sys

_sys.path.insert(0, str(APP_DIR))
_sys.path.insert(0, str(ROOT / "scripts"))
import knowledge  # noqa: E402
import llm  # noqa: E402
import markdown_render  # noqa: E402

STATIC = APP_DIR / "static"


class Handler(BaseHTTPRequestHandler):
    server_version = "LLMWiki/0.1"

    # ---------- helpers ----------
    def _send(self, status: int, body: bytes, ctype: str = "application/json; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, data) -> None:
        self._send(status, json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}

    def log_message(self, fmt: str, *args) -> None:  # quieter logs
        print(f"[http] {self.address_string()} {fmt % args}")

    # ---------- routing ----------
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            self._serve_static("index.html")
            return
        if path.startswith("/static/"):
            self._serve_static(path[len("/static/") :])
            return
        if path == "/api/health":
            return self._health()
        if path == "/api/search":
            return self._search(qs)
        if path == "/api/pages":
            return self._pages()
        if path == "/api/page":
            return self._page(qs)
        if path == "/api/raw":
            return self._raw(qs)
        if path == "/api/inbox":
            return self._inbox()
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)
        if path == "/api/ask":
            return self._ask(self._read_json())
        if path == "/api/ingest":
            return self._ingest(self._read_json(), qs)
        if path == "/api/render-md":
            data = self._read_json()
            return self._json(200, {"html": markdown_render.render(data.get("md", ""))})
        self._json(404, {"error": "not found"})

    # ---------- static ----------
    def _serve_static(self, name: str) -> None:
        target = (STATIC / name).resolve()
        if not str(target).startswith(str(STATIC.resolve())) or not target.is_file():
            return self._json(404, {"error": "not found"})
        ctype = {
            ".html": "text/html; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".svg": "image/svg+xml",
            ".png": "image/png",
        }.get(target.suffix.lower(), "application/octet-stream")
        self._send(200, target.read_bytes(), ctype)

    # ---------- API ----------
    def _health(self) -> None:
        self._json(
            200,
            {
                "ok": True,
                "wiki_pages": len(knowledge.load_wiki_index()),
                "raw_chapters": len(knowledge.load_raw_index()),
                "llm_configured": llm.configured(),
                "model": __import__("os").environ.get("OPENAI_MODEL", "未配置"),
            },
        )

    def _search(self, qs) -> None:
        query = (qs.get("q", [""])[0]).strip()
        raw = qs.get("raw", ["0"])[0] in ("1", "true", "yes")
        top = min(int(qs.get("top", ["8"])[0] or 8), 50)
        if not query:
            return self._json(400, {"error": "q 不能为空"})
        results = knowledge.search(query, raw=raw, top=top)
        self._json(200, {"query": query, "raw": raw, "results": results})

    def _pages(self) -> None:
        pages = [
            {"path": p["path"], "title": p["title"], "type": p["type"]}
            for p in knowledge.load_wiki_index()
        ]
        self._json(200, {"pages": pages})

    def _page(self, qs) -> None:
        path = qs.get("path", [""])[0]
        md = knowledge.page_markdown(path)
        if md is None:
            return self._json(404, {"error": "page not found"})
        fm, body = _split_frontmatter(md)
        self._json(
            200,
            {
                "path": path,
                "markdown": md,
                "html": markdown_render.render(body),
                "frontmatter": fm,
            },
        )

    def _raw(self, qs) -> None:
        path = qs.get("path", [""])[0]
        target = (ROOT / path).resolve()
        if (
            not str(target).startswith(str(ROOT.resolve()))
            or not target.is_file()
            or target.suffix not in (".htm", ".html")
        ):
            return self._json(404, {"error": "raw file not found"})
        from doc_text import html_to_text  # type: ignore

        text = html_to_text(target.read_bytes())
        self._json(200, {"path": path, "text": text[:20000]})

    def _ask(self, data: dict) -> None:
        question = (data.get("question") or "").strip()
        raw = bool(data.get("raw", False))
        if not question:
            return self._json(400, {"error": "question 不能为空"})
        wiki_hits = knowledge.search(question, raw=False, top=8)
        raw_hits = knowledge.search(question, raw=True, top=5) if raw else []
        citations = wiki_hits + raw_hits
        prompt = _build_prompt(question, citations)
        system = (
            "你是 Oracle EBS R12.2 知识库助手。只依据提供的资料回答，"
            "区分 T1（官方文档原文）与未验证推断；引用格式：[来源：<路径>]。"
            "资料不足时明确说不知道，不要编造。用中文回答。"
        )
        answer = llm.ask(system, prompt) if llm.configured() else None
        if answer:
            mode = "llm"
        else:
            mode = "local"
            answer = (
                "当前未配置 OPENAI_API_KEY，以下为本地检索结果（可复制下方 Prompt 交给 Codex 深入回答）：\n\n"
                + _local_answer(citations)
            )
        self._json(200, {"question": question, "mode": mode, "answer": answer, "citations": citations, "prompt": prompt})

    def _ingest(self, data: dict, qs) -> None:
        try:
            result = knowledge.ingest(
                data.get("title", ""),
                data.get("content", ""),
                data.get("source_url", ""),
                dry_run=qs.get("dry_run", ["0"])[0] in ("1", "true"),
            )
            self._json(200, result)
        except ValueError as exc:
            self._json(400, {"error": str(exc)})

    def _inbox(self) -> None:
        self._json(200, {"items": knowledge.list_inbox()})


class ThreadedApp(ThreadingHTTPServer):
    pass


def _split_frontmatter(md: str) -> tuple[dict, str]:
    fm: dict[str, str] = {}
    if not md.startswith("---"):
        return fm, md
    end = md.find("\n---", 3)
    if end < 0:
        return fm, md
    for line in md[4:end].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("[]")
    return fm, md[end + 4 :]


def _build_prompt(question: str, citations: list[dict]) -> str:
    ctx = []
    for i, c in enumerate(citations, 1):
        ctx.append(f"[{i}] {c.get('title','')} ({c.get('path','')})\n{c.get('snippet','')}")
    return (
        f"问题：{question}\n\n"
        "可参考资料：\n" + "\n\n".join(ctx) + "\n\n"
        "请基于资料回答；引用格式 [来源：<路径>]。资料不足请明说。"
    )


def _local_answer(citations: list[dict]) -> str:
    if not citations:
        return "本地检索没有找到相关资料。可以尝试换关键词，或在“补充知识”页加入内容。"
    lines = []
    for c in citations:
        lines.append(f"- **{c.get('title','')}**（{c.get('path','')}）\n  {c.get('snippet','')}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"LLM Wiki UI: http://{args.host}:{args.port}")
    print("LLM:", "已配置" if llm.configured() else "未配置（使用本地检索回答）")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


def main_serve(host: str, port: int) -> None:
    server = ThreadedApp((host, port), Handler)
    print(f"LLM Wiki UI: http://{host}:{port}")
    print("LLM:", "已配置" if llm.configured() else "未配置（使用本地检索回答）")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
