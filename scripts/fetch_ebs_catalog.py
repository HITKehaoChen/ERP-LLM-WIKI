"""
Fetch the Oracle E-Business Suite R12.2 Documentation Web Library catalog.

Outputs (bulk-generated, do not hand-edit):
  sources/catalog/ebs_r122_booklist.json
  sources/catalog/ebs_r122_booklist.csv
  sources/catalog/ebs_r122_areas.json

The booklist page itself is Oracle's "Current Booklist" for Release 12.2.
This script is idempotent; re-run it to refresh the catalog.
"""

from __future__ import annotations

import csv
import html as html_lib
import json
import re
import urllib.request
from pathlib import Path
from urllib.parse import urljoin

BASE = "https://docs.oracle.com/cd/E26401_01/"
BOOKLIST_URL = urljoin(BASE, "nav/portal_booklist.htm")
NAV_PAGES = [
    "technology.htm",
    "crm.htm",
    "service.htm",
    "financials.htm",
    "hcm.htm",
    "mdm.htm",
    "projects.htm",
    "procurement.htm",
    "g_invoicing.htm",
    "scm.htm",
    "vcp.htm",
    "vce.htm",
]

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CATALOG_DIR = ROOT / "sources" / "catalog"
CATALOG_DIR.mkdir(parents=True, exist_ok=True)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read().decode("utf-8", "ignore")


def clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_lib.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def parse_booklist(html: str) -> list[dict]:
    books = []
    for block in re.finditer(
        r'<div class="booklist">(.*?)</div>\s*</div>\s*</div>', html, re.S
    ):
        raw = block.group(1)
        title_m = re.search(r'class="booktitle"><a href="([^"]+)"[^>]*>(.*?)</a>', raw, re.S)
        if not title_m:
            continue
        toc_url = urljoin(BASE, title_m.group(1))
        title = clean(title_m.group(2))
        info_m = re.search(r'class="bookinfo shadow">(.*?)<b class="notch">', raw, re.S)
        pdf_m = re.search(r'<a href="([^"]+\.pdf)"', raw, re.I)
        part_m = re.search(r"doc\.122/([a-z0-9]+)", toc_url, re.I)
        legacy_broken = "/h/uaework/tmp/archive/" in toc_url
        pdf_url = urljoin(BASE, pdf_m.group(1)) if pdf_m else ""
        if not pdf_url and part_m:
            # Legacy booklist entries omit the PDF link; the standard path works.
            pdf_url = urljoin(BASE, f"doc.122/{part_m.group(1).lower()}.pdf")
        books.append(
            {
                "title": title,
                "part_number": part_m.group(1).lower() if part_m else "",
                "toc_url": toc_url,
                "toc_url_status": "legacy_broken" if legacy_broken else "ok",
                "pdf_url": pdf_url,
                "description": clean(info_m.group(1)) if info_m else "",
            }
        )
    return books


def parse_nav(html: str) -> list[dict]:
    links = []
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.S):
        href, text = m.group(1), clean(m.group(2))
        if not text or ("toc.htm" not in href and "pdf" not in href.lower()):
            continue
        full = urljoin(BASE, href)
        part_m = re.search(r"doc\.122/([a-z0-9]+)", full, re.I)
        links.append(
            {
                "part_number": part_m.group(1).lower() if part_m else "",
                "title": text,
                "url": full,
            }
        )
    return links


def main() -> None:
    booklist_html = fetch(BOOKLIST_URL)
    books = parse_booklist(booklist_html)
    print(f"booklist entries: {len(books)}")

    areas = {}
    for page in NAV_PAGES:
        url = urljoin(BASE, "nav/" + page)
        try:
            html = fetch(url)
        except Exception as exc:  # noqa: BLE001
            print(f"WARN {page}: {exc}")
            continue
        area = page.removesuffix(".htm")
        for link in parse_nav(html):
            part = link["part_number"]
            if part:
                areas.setdefault(part, {"part_number": part, "areas": set()})
                areas[part]["areas"].add(area)
    for item in areas.values():
        item["areas"] = sorted(item["areas"])

    (CATALOG_DIR / "ebs_r122_booklist.json").write_text(
        json.dumps(books, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (CATALOG_DIR / "ebs_r122_areas.json").write_text(
        json.dumps(list(areas.values()), ensure_ascii=False, indent=2), encoding="utf-8"
    )

    with (CATALOG_DIR / "ebs_r122_booklist.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "part_number",
                "title",
                "description",
                "toc_url",
                "toc_url_status",
                "pdf_url",
            ],
        )
        writer.writeheader()
        writer.writerows(books)

    print(f"area mappings: {len(areas)}")
    print("written to", CATALOG_DIR)


if __name__ == "__main__":
    main()
