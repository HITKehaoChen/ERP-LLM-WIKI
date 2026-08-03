"""
Generate one wiki page per priority Oracle EBS R12.2 document.

Reads sources/catalog/priority_docs.json + ebs_r122_booklist.json and writes:
  wiki/sources/<part>.md
  wiki/sources/index.md

These are bulk-generated starting points; the LLM may later enrich them with
chapter-level notes, but the metadata block must stay in sync with the raw
catalog (re-run this script after refreshing the catalog).
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CATALOG_DIR = ROOT / "sources" / "catalog"
WIKI_SOURCES = ROOT / "wiki" / "sources"
WIKI_SOURCES.mkdir(parents=True, exist_ok=True)

AREA_NAMES = {
    "wip": "WIP / 离散制造",
    "inventory": "Inventory / 库存",
    "order-management": "Order Management / 销售订单",
    "intercompany": "Intercompany / 关联交易与财务",
    "foundation": "Foundation / 基础与技术",
}


def rel_from_sources(part: str, filename: str) -> str:
    return f"../../sources/docs/{part}/{filename}"


def toc_markdown(toc: list[dict]) -> str:
    if not toc:
        return "_本文档仅发布 PDF，无 HTML 章节树。_"
    lines = []
    for node in toc:
        text = node["text"].replace("|", "\\|")
        indent = "  " * node["level"]
        lines.append(f"{indent}- {text}")
    return "\n".join(lines)


def main() -> None:
    priority = json.loads((CATALOG_DIR / "priority_docs.json").read_text(encoding="utf-8"))
    booklist = json.loads((CATALOG_DIR / "ebs_r122_booklist.json").read_text(encoding="utf-8"))
    book_by_part = {b["part_number"]: b for b in booklist}

    pages = []
    for rec in priority["records"]:
        part = rec["part_number"]
        book = book_by_part.get(part, {})
        toc_status = rec.get("toc_status", "")
        status_hint = (
            "HTML 已失效，PDF 快照可用"
            if toc_status == "html_unavailable_pdf_ok"
            else "HTML+PDF 可用"
        )
        lines = [
            "---",
            f"title: \"{rec['title']}\"",
            "type: source",
            f"part_number: {part}",
            f"part_number_full: \"{rec.get('part_number_full') or ''}\"",
            f"release: \"{rec.get('release') or '12.2'}\"",
            f"area: {rec.get('area')}",
            "status: cataloged",
            "verified: doc-only",
            f"fetched_at: {rec.get('fetched_at', '')}",
            f"toc_status: {toc_status}",
            "tags: [" + ", ".join(rec.get("tags", [])) + "]",
            "---",
            "",
            f"# {rec['title']}",
            "",
            "## 文档元数据",
            "",
            "| 字段 | 值 |",
            "| --- | --- |",
            f"| 产品域 | {AREA_NAMES.get(rec.get('area'), rec.get('area'))} |",
            f"| Part Number | {rec.get('part_number_full') or '（书单无完整号）'} |",
            f"| Release | {rec.get('release') or '12.2'} |",
            f"| 修订日期 | {rec.get('date_modified') or '未知（HTML 不可用）'} |",
            f"| 版权年份 | {rec.get('copyright') or '-'} |",
            f"| 状态 | {status_hint} |",
            f"| 抓取时间 | {rec.get('fetched_at', '')} |",
            "",
            "## 链接与证据",
            "",
            f"- HTML 目录: [{rec['toc_url']}]({rec['toc_url']})"
            + ("（当前失效）" if toc_status == "html_unavailable_pdf_ok" else ""),
            f"- PDF: [{rec.get('pdf_url')}]({rec.get('pdf_url')})",
            f"- 原始快照 (raw 层): [toc.html]({rel_from_sources(part, 'toc.html')})"
            if toc_status == "ok"
            else f"- 原始快照 (raw 层): [{part}.pdf]({rel_from_sources(part, part + '.pdf')})",
            "",
            f"> 官方描述：{book.get('description') or rec.get('title')}",
            "",
            "## 章节树（来自官方 TOC 快照）",
            "",
            toc_markdown(rec.get("toc", [])),
            "",
        ]
        (WIKI_SOURCES / f"{part}.md").write_text("\n".join(lines), encoding="utf-8")
        pages.append(rec)

    by_area: dict[str, list[dict]] = {}
    for rec in pages:
        by_area.setdefault(rec["area"], []).append(rec)

    idx = [
        "---",
        "title: 来源页索引（重点文档）",
        "type: index",
        "status: stable",
        "updated: " + date.today().isoformat(),
        "---",
        "",
        "# 来源页索引",
        "",
        f"共 {len(pages)} 份重点文档，按产品域分组。原始快照位于 `sources/docs/`，本文档由 `scripts/build_wiki_sources.py` 生成。",
        "",
    ]
    for area in sorted(by_area):
        idx.append(f"## {AREA_NAMES.get(area, area)}（{len(by_area[area])}）")
        idx.append("")
        for rec in sorted(by_area[area], key=lambda r: r["title"].lower()):
            idx.append(f"- [{rec['title']}]({rec['part_number']}.md) — `{rec['part_number_full'] or rec['part_number']}`")
        idx.append("")
    (WIKI_SOURCES / "index.md").write_text("\n".join(idx), encoding="utf-8")
    print(f"wrote {len(pages)} source pages + index to {WIKI_SOURCES}")


if __name__ == "__main__":
    main()
