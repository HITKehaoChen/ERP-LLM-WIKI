"""Knowledge layer: loads wiki + raw chapter indexes and answers local queries."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
SOURCES = ROOT / "sources"
INBOX = SOURCES / "inbox"
WIKI_INDEX = WIKI / "search-index.json"
RAW_INDEX = SOURCES / "catalog" / "raw_index.json"

STOP = {
    "the", "a", "an", "of", "in", "on", "to", "for", "and", "or", "is", "are",
    "的", "了", "与", "和", "在", "是", "等", "及",
}


_LATIN = re.compile(r"[a-z0-9_]+")
_CJK = re.compile(r"[\u4e00-\u9fff]")


def tokens(text: str) -> list[str]:
    """Tokenize for Chinese-friendly search.

    Latin words are kept whole; CJK text is split into character bigrams
    (plus single characters) so natural-language questions like
    "OM模块的业务流程是什么样子的" match pages containing "业务流程".
    """
    low = text.lower()
    out: list[str] = []
    for m in _LATIN.finditer(low):
        t = m.group(0)
        if t not in STOP:
            out.append(t)
    chars = _CJK.findall(low)
    for i in range(len(chars)):
        if i + 1 < len(chars):
            out.append(chars[i] + chars[i + 1])
        out.append(chars[i])
    seen: set[str] = set()
    return [t for t in out if not (t in seen or seen.add(t))]


def load_wiki_index() -> list[dict]:
    if not WIKI_INDEX.exists():
        return []
    return json.loads(WIKI_INDEX.read_text(encoding="utf-8"))


def load_raw_index() -> list[dict]:
    if not RAW_INDEX.exists():
        return []
    return json.loads(RAW_INDEX.read_text(encoding="utf-8"))


def _score(entry: dict, q_tokens: list[str]) -> tuple[float, str]:
    title = entry.get("title", "")
    body = entry.get("body", "")
    score = 0.0
    for t in q_tokens:
        if t in title.lower():
            score += 8
        score += body.lower().count(t)
    if score <= 0:
        return 0.0, ""
    low = body.lower()
    first = min((low.find(t) for t in q_tokens if low.find(t) >= 0), default=-1)
    snippet = body[max(0, first - 100) : first + 240].replace("\n", " ").strip()
    return score, snippet


def search(query: str, raw: bool = False, top: int = 8) -> list[dict]:
    q = tokens(query)
    if not q:
        return []
    results = []
    for entry in load_wiki_index():
        score, snippet = _score(entry, q)
        if score > 0:
            results.append(
                {
                    "score": round(score, 1),
                    "path": entry.get("path"),
                    "title": entry.get("title"),
                    "type": entry.get("type", ""),
                    "kind": "wiki",
                    "snippet": snippet,
                }
            )
    if raw:
        for entry in load_raw_index():
            score, snippet = _score(entry, q)
            if score > 0:
                results.append(
                    {
                        "score": round(score, 1),
                        "path": entry.get("path"),
                        "title": entry.get("title"),
                        "type": "raw",
                        "kind": "raw",
                        "snippet": snippet,
                    }
                )
    results.sort(key=lambda r: -r["score"])
    return results[:top]


def page_markdown(path: str) -> str | None:
    """Return markdown for a repo-relative .md path (wiki or inbox or sources)."""
    target = (ROOT / path).resolve()
    if not target.is_relative_to(ROOT.resolve()) or target.suffix != ".md":
        return None
    if not target.exists():
        return None
    return target.read_text(encoding="utf-8", errors="ignore")


def ingest(title: str, content: str, source_url: str = "", dry_run: bool = False) -> dict:
    title = _clean_fm(title)
    source_url = _clean_fm(source_url)
    if not title or not content.strip():
        raise ValueError("标题与内容不能为空")
    if len(content) > 200_000:
        raise ValueError("内容过长（上限 200KB）")
    INBOX.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^\w\u4e00-\u9fff]+", "-", title).strip("-").lower() or "untitled"
    fname = f"{date.today().isoformat()}-{slug[:60]}.md"
    path = _next_available_path(INBOX / fname)
    fm = [
        "---",
        f"title: {_yaml(title)}",
        "type: inbox",
        "status: pending-ingest",
        f"source_url: {_yaml(source_url)}",
        f"created: {date.today().isoformat()}",
        "---",
        "",
    ]
    body = content.strip()
    markdown = "\n".join(fm) + body + "\n"
    log_line = (
        f"## [{date.today().isoformat()}] ingest-inbox | {title.strip()}\n"
        f"- 通过网页补充：`{path.relative_to(ROOT).as_posix()}`"
        + (f"（来源：{source_url.strip()}）" if source_url.strip() else "")
        + "\n"
    )
    if dry_run:
        return {"path": path.relative_to(ROOT).as_posix(), "log_line": log_line, "dry_run": True}
    path.write_text(markdown, encoding="utf-8")
    log = WIKI / "log.md"
    with log.open("a", encoding="utf-8") as fh:
        fh.write("\n" + log_line)
    return {"path": path.relative_to(ROOT).as_posix(), "log_line": log_line, "dry_run": False}


def _clean_fm(value: str) -> str:
    return re.sub(r"[\r\n\t\x00-\x1f]", " ", value or "").strip()


def _yaml(value: str) -> str:
    """Quote frontmatter values as JSON strings (valid YAML, safely escaped)."""
    return json.dumps(value, ensure_ascii=False)


def _next_available_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    for i in range(2, 1000):
        candidate = path.with_name(f"{stem}-{i}{suffix}")
        if not candidate.exists():
            return candidate
    raise ValueError("无法生成不重复的文件名")


def list_inbox() -> list[dict]:
    if not INBOX.exists():
        return []
    items = []
    for p in sorted(INBOX.glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm, _ = _split_fm(text)
        items.append(
            {
                "path": p.relative_to(ROOT).as_posix(),
                "title": fm.get("title", p.stem),
                "status": fm.get("status", ""),
                "source_url": fm.get("source_url", ""),
                "created": fm.get("created", ""),
            }
        )
    return items


def _split_fm(md: str) -> tuple[dict, str]:
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


def build_graph() -> dict:
    """Build a knowledge graph: wiki pages as nodes, markdown links as edges."""
    pages = load_wiki_index()
    by_path = {p["path"]: p for p in pages}
    nodes = []
    for p in pages:
        nodes.append(
            {
                "id": p["path"],
                "title": p.get("title", ""),
                "type": p.get("type", ""),
            }
        )
    id_set = {n["id"] for n in nodes}
    links = []
    seen = set()
    for p in pages:
        md = page_markdown(p["path"]) or ""
        _, body = _split_fm(md)
        page_dir = (ROOT / p["path"]).parent
        for m in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", body):
            target = m.group(1).split("#", 1)[0].strip()
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved_path = (page_dir / target).resolve()
            try:
                resolved = str(resolved_path.relative_to(ROOT)).replace("\\", "/")
            except ValueError:
                continue
            if resolved not in id_set or resolved == p["path"]:
                continue
            key = tuple(sorted((p["path"], resolved)))
            if key in seen:
                continue
            seen.add(key)
            links.append({"source": p["path"], "target": resolved})
    # node size by inbound degree
    degree = {n["id"]: 0 for n in nodes}
    for l in links:
        degree[l["target"]] += 1
    for n in nodes:
        n["size"] = 3 + min(degree[n["id"]], 15)
    return {"nodes": nodes, "links": links}
