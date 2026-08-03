"""
Full-text search over the LLM Wiki (and optionally the raw Oracle chapters).

Usage:
  python scripts/search_wiki.py "WIP job statuses"          # wiki pages only
  python scripts/search_wiki.py "order line status" --raw    # + raw chapter text
  python scripts/search_wiki.py --build-index                # write wiki/search-index.json
  python scripts/search_wiki.py --build-raw-index            # write sources/catalog/raw_index.json
  python scripts/search_wiki.py "invoice interface" --top 5

Ranking: title hits > frontmatter tags > headings > body hits.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
SOURCES = ROOT / "sources" / "docs"
CATALOG = ROOT / "sources" / "catalog"

STOP = {
    "the", "a", "an", "of", "in", "on", "to", "for", "and", "or", "is", "are",
    "的", "了", "与", "和", "在", "是", "等", "及",
}


def tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[\w\u4e00-\u9fff]+", text.lower()) if t not in STOP]


def load_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    fm: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("[]")
    return fm, text[end + 4 :]


def wiki_pages() -> list[dict]:
    pages = []
    for p in sorted(WIKI.rglob("*.md")):
        if p.name == "log.md":
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm, body = load_frontmatter(text)
        rel = p.relative_to(ROOT).as_posix()
        pages.append(
            {
                "path": rel,
                "title": fm.get("title", p.stem),
                "type": fm.get("type", ""),
                "tags": fm.get("tags", ""),
                "body": body,
                "text": text,
            }
        )
    return pages


def raw_chapters() -> list[dict]:
    items = []
    for p in sorted(SOURCES.glob("*/chapters/*.htm")):
        text = p.read_text(encoding="utf-8", errors="ignore")
        # crude strip for search purposes
        text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", text, flags=re.S)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        items.append(
            {
                "path": p.relative_to(ROOT).as_posix(),
                "title": f"{p.parent.parent.name} / {p.stem}",
                "body": text,
                "text": text,
            }
        )
    return items


def score_page(page: dict, q_tokens: list[str]) -> tuple[float, str]:
    title = page.get("title", "")
    tags = page.get("tags", "")
    body = page.get("body", "")
    heading_lines = [l for l in body.splitlines() if l.startswith("#")]
    headings = "\n".join(heading_lines)
    score = 0.0
    for t in q_tokens:
        if t in title.lower():
            score += 10
        if t in tags.lower():
            score += 5
        if t in headings.lower():
            score += 3
        score += body.lower().count(t)
    if score <= 0:
        return 0, ""
    # first hit snippet
    low = body.lower()
    first = min((low.find(t) for t in q_tokens if low.find(t) >= 0), default=-1)
    snippet = body[max(0, first - 90) : first + 190].replace("\n", " ").strip()
    return score, snippet


def build_index() -> Path:
    pages = wiki_pages()
    out = [
        {
            "path": p["path"],
            "title": p["title"],
            "type": p["type"],
            "tags": p["tags"],
            "body": p["body"][:8000],
        }
        for p in pages
    ]
    target = WIKI / "search-index.json"
    target.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"index written: {target} ({len(out)} pages)")
    return target


def build_raw_index() -> Path:
    items = []
    for p in sorted(SOURCES.glob("*/chapters/*.htm")):
        text = p.read_text(encoding="utf-8", errors="ignore")
        text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", text, flags=re.S)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        items.append(
            {
                "path": p.relative_to(ROOT).as_posix(),
                "title": f"{p.parent.parent.name} / {p.stem}",
                "body": text[:40000],
            }
        )
    target = CATALOG / "raw_index.json"
    CATALOG.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"raw index written: {target} ({len(items)} chapters)")
    return target


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", default="")
    ap.add_argument("--raw", action="store_true", help="include raw chapter HTML text")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--build-index", action="store_true")
    ap.add_argument("--build-raw-index", action="store_true")
    args = ap.parse_args()

    if args.build_index:
        build_index()
        return 0
    if args.build_raw_index:
        build_raw_index()
        return 0
    if not args.query:
        ap.print_help()
        return 2

    q_tokens = tokens(args.query)
    if not q_tokens:
        print("query has no searchable tokens")
        return 2

    pages = wiki_pages()
    if args.raw:
        pages += raw_chapters()
    results = []
    for page in pages:
        score, snippet = score_page(page, q_tokens)
        if score > 0:
            results.append((score, page["path"], page.get("title", ""), snippet))
    results.sort(key=lambda r: -r[0])
    print(f"found {len(results)} match(es)\n")
    for score, path, title, snippet in results[: args.top]:
        print(f"[{score:.1f}] {path}")
        if title:
            print(f"      {title}")
        if snippet:
            print(f"      …{snippet}…")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
