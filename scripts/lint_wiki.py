"""
Health-check the LLM Wiki.

Checks:
  1. Broken internal markdown links (wiki/ + top-level README/AGENTS/llms.txt).
  2. Orphan wiki pages (no inbound link from another wiki page).
  3. Log entry prefix format in wiki/log.md.
  4. Frontmatter presence for wiki content pages.
  5. Contradiction block count (informational).

Exit code 0 = clean, 1 = issues found.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
TOP_FILES = ["README.md", "AGENTS.md", "llms.txt"]

SCAN_FILES = sorted(
    [p for p in WIKI.rglob("*.md") if p.name not in {"log.md"}]
    + [ROOT / f for f in TOP_FILES]
)
ALL_MD = {p.resolve() for p in WIKI.rglob("*.md")}
ALL_MD |= { (ROOT / f).resolve() for f in TOP_FILES }

issues: list[str] = []


def resolve_link(base: Path, target: str) -> Path | None:
    target = target.split("#", 1)[0].strip()
    if not target or target.startswith(("http://", "https://", "mailto:")):
        return None
    if target.startswith("/"):
        return (ROOT / target.lstrip("/")).resolve()
    return (base / unquote(target)).resolve()


def inbound_count() -> dict[Path, int]:
    counts: dict[Path, int] = {}
    for file in SCAN_FILES:
        text = file.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
            link = m.group(1)
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
            resolved = resolve_link(file.parent, link)
            if resolved and resolved in ALL_MD:
                counts[resolved] = counts.get(resolved, 0) + 1
    return counts


def main() -> int:
    # 1. broken links
    for file in SCAN_FILES:
        text = file.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
            link = m.group(1)
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
            resolved = resolve_link(file.parent, link)
            if resolved is None:
                continue
            if not resolved.exists():
                rel = file.relative_to(ROOT)
                issues.append(f"broken link in {rel}: -> {link} (resolved {resolved})")

    # 2. orphans
    counts = inbound_count()
    wiki_pages = {p.resolve() for p in WIKI.rglob("*.md")}
    for page in sorted(wiki_pages):
        if counts.get(page, 0) == 0:
            issues.append(f"orphan page: {page.relative_to(ROOT)}")

    # 3. log format
    log = (WIKI / "log.md").read_text(encoding="utf-8", errors="ignore")
    bad_log = [
        line
        for line in log.splitlines()
        if line.startswith("## [") and not re.match(r"^## \[\d{4}-\d{2}-\d{2}\]", line)
    ]
    for line in bad_log:
        issues.append(f"bad log prefix: {line}")

    # 4. frontmatter
    for page in sorted(WIKI.rglob("*.md")):
        if page.name == "log.md":
            continue
        head = page.read_text(encoding="utf-8", errors="ignore")[:200]
        if not head.startswith("---"):
            issues.append(f"missing frontmatter: {page.relative_to(ROOT)}")

    # 5. contradictions (informational)
    contra = 0
    for page in WIKI.rglob("*.md"):
        text = page.read_text(encoding="utf-8", errors="ignore")
        contra += text.count("> [!contradiction]")

    if issues:
        print(f"LINT: {len(issues)} issue(s) found")
        for issue in issues:
            print(" -", issue)
        return 1
    print(f"LINT OK: {len(SCAN_FILES)} files checked, no issues. "
          f"({contra} contradiction block(s) present)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
