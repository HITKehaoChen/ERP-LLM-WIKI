"""
Fetch the full HTML chapter pages for priority Oracle EBS R12.2 documents.

For each requested part number this reads the already-fetched TOC snapshot,
resolves every unique chapter file, downloads it, and writes:
  sources/docs/<part>/chapters/<chapter-file>.html
  sources/catalog/chapters_<part>.json   (chapter -> title mapping + fetch status)

Usage:
  python scripts/fetch_chapters.py e48843 e48905 ...
  python scripts/fetch_chapters.py --all-priority
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DOC_BASE = "https://docs.oracle.com/cd/E26401_01/doc.122"
SKIP_FILES = {"title.htm", "rcf.htm", "index.htm"}

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DOCS_DIR = ROOT / "sources" / "docs"
CATALOG_DIR = ROOT / "sources" / "catalog"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def main() -> None:
    args = [a for a in sys.argv[1:]]
    if not args:
        print(__doc__)
        sys.exit(2)
    if "--all-priority" in args:
        priority = json.loads((CATALOG_DIR / "priority_docs.json").read_text(encoding="utf-8"))
        parts = [r["part_number"] for r in priority["records"]]
    else:
        parts = [a for a in args if not a.startswith("--")]

    for part in parts:
        priority = json.loads((CATALOG_DIR / "priority_docs.json").read_text(encoding="utf-8"))
        rec = next(r for r in priority["records"] if r["part_number"] == part)
        toc = rec.get("toc", [])
        chapters: dict[str, str] = {}
        for node in toc:
            file = node["href"].split("#", 1)[0]
            if file in SKIP_FILES or not file.endswith(".htm"):
                continue
            chapters.setdefault(file, node["text"])

        chapter_dir = DOCS_DIR / part / "chapters"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        results = []
        for file, title in sorted(chapters.items()):
            url = f"{DOC_BASE}/{part}/{file}"
            target = chapter_dir / file
            try:
                data = fetch(url)
                target.write_bytes(data)
                status = "ok"
                size = len(data)
            except Exception as exc:  # noqa: BLE001
                status = f"error: {exc}"
                size = 0
            results.append(
                {
                    "file": file,
                    "title": title,
                    "url": url,
                    "status": status,
                    "size": size,
                    "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                }
            )
            print(f"{part} {file} {status} {size}")

        (CATALOG_DIR / f"chapters_{part}.json").write_text(
            json.dumps(
                {
                    "part_number": part,
                    "title": rec["title"],
                    "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "chapters": results,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        ok = sum(1 for r in results if r["status"] == "ok")
        print(f"== {part}: {ok}/{len(results)} chapters fetched -> {chapter_dir}")


if __name__ == "__main__":
    main()
