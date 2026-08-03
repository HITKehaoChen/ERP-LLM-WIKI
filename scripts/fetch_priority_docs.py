"""
Fetch metadata + raw TOC snapshots for the priority Oracle EBS R12.2 documents.

Priority domains (per project focus): WIP / Inventory / Order Management /
Intercompany & Financials / Foundation & Technology.

For each document this writes:
  sources/docs/<part>/toc.html      raw TOC snapshot (immutable raw layer)
  sources/docs/<part>/title.html    raw title/copyright snapshot
and one merged machine-readable record:
  sources/catalog/priority_docs.json

Re-running refreshes the snapshots and records the new fetch date.
"""

from __future__ import annotations

import html as html_lib
import json
import re
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

DOC_BASE = "https://docs.oracle.com/cd/E26401_01/doc.122"

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DOCS_DIR = ROOT / "sources" / "docs"
CATALOG_DIR = ROOT / "sources" / "catalog"
DOCS_DIR.mkdir(parents=True, exist_ok=True)
CATALOG_DIR.mkdir(parents=True, exist_ok=True)

# part_number -> (area, tags)
PRIORITY = {
    # WIP / Discrete Manufacturing
    "e48905": ("wip", ["wip", "discrete-manufacturing"]),
    "e48954": ("wip", ["bom", "manufacturing"]),
    "e48829": ("wip", ["cost-management", "manufacturing"]),
    "e48906": ("wip", ["mes", "manufacturing"]),
    "e48944": ("wip", ["shop-floor-management", "manufacturing"]),
    "e48953": ("wip", ["outsourced-manufacturing", "manufacturing"]),
    "e48907": ("wip", ["flow-manufacturing", "manufacturing"]),
    "e53484": ("wip", ["in-memory-cost", "manufacturing"]),
    "e48939": ("wip", ["engineering", "manufacturing"]),
    "e48959": ("wip", ["quality", "manufacturing"]),
    "e48961": ("wip", ["quality", "manufacturing"]),
    "e48945": ("wip", ["manufacturing-operations-center"]),
    "e48947": ("wip", ["manufacturing-operations-center"]),
    # Inventory / Value Chain Execution
    "e48820": ("inventory", ["inv", "vce"]),
    "e48822": ("inventory", ["inv", "consigned-inventory"]),
    "e48823": ("inventory", ["inv", "implementation"]),
    "e48824": ("inventory", ["inv", "movement-statistics"]),
    "e48828": ("inventory", ["wms", "implementation"]),
    "e48830": ("inventory", ["wms", "vce"]),
    "e48825": ("inventory", ["msca", "implementation"]),
    "e48826": ("inventory", ["msca", "vce"]),
    "e48799": ("inventory", ["landed-cost", "process-guide"]),
    "e53453": ("inventory", ["yard-management", "process-guide"]),
    # Order Management
    "e48843": ("order-management", ["om", "user-guide"]),
    "e48842": ("order-management", ["om", "implementation"]),
    "e48844": ("order-management", ["om", "workflow"]),
    "e48847": ("order-management", ["shipping", "user-guide"]),
    "e48846": ("order-management", ["advanced-pricing", "implementation"]),
    "e48845": ("order-management", ["advanced-pricing", "user-guide"]),
    "e48832": ("order-management", ["configure-to-order", "process-guide"]),
    "e48848": ("order-management", ["release-management", "implementation"]),
    "e48849": ("order-management", ["release-management", "user-guide"]),
    # Intercompany / Financials
    "e48781": ("intercompany", ["agis", "intercompany", "user-guide"]),
    "e48783": ("intercompany", ["financials", "implementation"]),
    "e48836": ("intercompany", ["financials", "concepts"]),
    "e48747": ("intercompany", ["gl", "implementation"]),
    "e48748": ("intercompany", ["gl", "user-guide"]),
    "e48749": ("intercompany", ["gl", "reference"]),
    "e48761": ("intercompany", ["ap", "implementation"]),
    "e48760": ("intercompany", ["ap", "user-guide"]),
    "e48763": ("intercompany", ["ap", "reference"]),
    "f10310": ("intercompany", ["ar", "implementation"]),
    "f10570": ("intercompany", ["ar", "user-guide"]),
    "f10312": ("intercompany", ["ar", "reference"]),
    "e48771": ("intercompany", ["sla", "subledger-accounting", "implementation"]),
    "e48750": ("intercompany", ["eb-tax", "implementation"]),
    "e48751": ("intercompany", ["eb-tax", "user-guide"]),
    "e48768": ("intercompany", ["payments", "implementation"]),
    "e48766": ("intercompany", ["payments", "user-guide"]),
    # Foundation / Technology
    "e22949": ("foundation", ["concepts", "ebs-core"]),
    "e22956": ("foundation", ["user-guide", "ebs-core"]),
    "e48833": ("foundation", ["multi-org", "implementation"]),
    "e22961": ("foundation", ["developer", "technology"]),
    "e22963": ("foundation", ["flexfields", "technology"]),
    "e22008": ("foundation", ["workflow", "administrator"]),
    "e22011": ("foundation", ["workflow", "developer"]),
    "e20923": ("foundation", ["soa-gateway", "user"]),
    "e20925": ("foundation", ["soa-gateway", "implementation"]),
    "e20927": ("foundation", ["soa-gateway", "developer"]),
    "f53031": ("foundation", ["etrm", "technical"]),
    "e22950": ("foundation", ["install", "rapid-install"]),
    "e87011": ("foundation", ["upgrade", "11i-to-12.2"]),
    "e73540": ("foundation", ["upgrade", "12.0-12.1-to-12.2"]),
}


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_lib.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def parse_title(title_html: str) -> dict:
    text = clean(title_html)
    title_m = re.search(
        r"(?:<title>|Oracle[^<]*?Guide|Oracle[^<]*?Manual|Oracle[^<]*?Reference)",
        title_html,
        re.I,
    )
    # Title is the first h1/h2 heading in the body.
    heading = re.search(r"<h[12][^>]*>(.*?)</h[12]>", title_html, re.S)
    title = clean(heading.group(1)) if heading else ""
    if not title:
        tm = re.search(r"<title>(.*?)</title>", title_html, re.S)
        title = clean(tm.group(1)) if tm else ""
    return {
        "title": title,
        "release": _first(r"Release\s+([0-9][0-9.]*)", text),
        "part_number_full": _first(r"Part Number\s+([A-Z0-9-]+)", text),
        "copyright": _first(r"Copyright\s+©\s+([0-9]{4}(?:,\s*[0-9]{4})?)", text),
        "primary_author": _first(r"Primary Author:\s*([^.]+)", text),
    }


def _first(pattern: str, text: str) -> str:
    m = re.search(pattern, text, re.I)
    return m.group(1).strip() if m else ""


def parse_toc(toc_html: str) -> list[dict]:
    """Parse the standard Oracle doc TOC into a chapter/section tree."""
    nodes: list[dict] = []
    chapters = re.finditer(
        r"<p><strong><a href=\"([^\"]+)\"[^>]*>(.*?)</a></strong></p>", toc_html, re.S
    )
    sections = re.finditer(r"<dd>(.*?)</dd>", toc_html, re.S)
    chapter_hrefs = {m.group(1) for m in chapters}
    # Re-scan with positions: chapters and sections appear in document order.
    pattern = re.compile(
        r"<p><strong><a href=\"([^\"]+)\"[^>]*>(.*?)</a></strong></p>|"
        r"<dd>(.*?)</dd>",
        re.S,
    )
    for m in pattern.finditer(toc_html):
        if m.group(1):
            nodes.append(
                {
                    "level": 0,
                    "text": clean(m.group(2)),
                    "href": m.group(1),
                }
            )
        else:
            raw = m.group(3)
            href_m = re.search(r'href="([^"]+)"[^>]*>(.*?)</a>', raw, re.S)
            if not href_m:
                continue
            text = clean(href_m.group(2))
            nbsp = raw.count("&nbsp;")
            nodes.append(
                {
                    "level": min(nbsp // 5, 3),
                    "text": text,
                    "href": href_m.group(1),
                }
            )
    return nodes


def title_from_booklist(part: str) -> str:
    booklist = json.loads((CATALOG_DIR / "ebs_r122_booklist.json").read_text(encoding="utf-8"))
    for book in booklist:
        if book["part_number"] == part:
            return book["title"]
    return part


def main() -> None:
    records = []
    for part, (area, tags) in sorted(PRIORITY.items()):
        part_dir = DOCS_DIR / part
        part_dir.mkdir(parents=True, exist_ok=True)
        toc_url = f"{DOC_BASE}/{part}/toc.htm"
        title_url = f"{DOC_BASE}/{part}/title.htm"
        pdf_url = f"{DOC_BASE}/{part}.pdf"
        try:
            toc_bytes = fetch(toc_url)
            title_bytes = fetch(title_url)
            toc_html = toc_bytes.decode("utf-8", "ignore")
            title_html = title_bytes.decode("utf-8", "ignore")
            toc_status = "ok"
            pdf_snapshot = False
        except Exception as exc:  # noqa: BLE001
            # Fallback: some docs only publish a PDF (HTML path retired).
            try:
                pdf_bytes = fetch(pdf_url)
            except Exception:  # noqa: BLE001
                print(f"WARN {part}: HTML and PDF unavailable ({exc})")
                continue
            (part_dir / f"{part}.pdf").write_bytes(pdf_bytes)
            toc_html = ""
            title_html = ""
            toc_status = "html_unavailable_pdf_ok"
            pdf_snapshot = True
            print(f"PDF-ONLY {part}: {pdf_url}")
        if toc_html:
            (part_dir / "toc.html").write_bytes(toc_bytes)
            (part_dir / "title.html").write_bytes(title_bytes)
        meta = parse_title(title_html)
        pub_m = re.search(r'"datePublished":"([^"]+)"', toc_html) if toc_html else None
        mod_m = re.search(r'"dateModified":"([^"]+)"', toc_html) if toc_html else None
        toc_nodes = parse_toc(toc_html) if toc_html else []
        if not meta.get("title"):
            meta["title"] = title_from_booklist(part)
        records.append(
            {
                "part_number": part,
                "part_number_full": meta.get("part_number_full") or "",
                "title": meta.get("title") or "",
                "release": meta.get("release") or "12.2",
                "copyright": meta.get("copyright") or "",
                "primary_author": meta.get("primary_author") or "",
                "date_published": pub_m.group(1) if pub_m else "",
                "date_modified": mod_m.group(1) if mod_m else "",
                "toc_status": toc_status,
                "pdf_snapshot": pdf_snapshot,
                "area": area,
                "tags": tags,
                "toc_url": toc_url,
                "title_url": title_url,
                "pdf_url": pdf_url,
                "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "toc": toc_nodes,
            }
        )
        if toc_html:
            print(f"OK {part:8s} {meta.get('title','')[:60]}  ({len(toc_nodes)} toc nodes)")

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "note": "Priority Oracle EBS R12.2 documents; raw snapshots under sources/docs/.",
        "records": records,
    }
    (CATALOG_DIR / "priority_docs.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n{len(records)}/{len(PRIORITY)} documents fetched.")


if __name__ == "__main__":
    main()
