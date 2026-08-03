"""Convert Oracle EBS HTML doc pages into readable text (tables preserved)."""

from __future__ import annotations

import re
from html.parser import HTMLParser


class _Extractor(HTMLParser):
    BLOCK = {"p", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "br", "dd", "dt"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.in_script = 0
        self.in_table = 0
        self.in_cell = False
        self.pending_space = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style"):
            self.in_script += 1
        elif tag == "table":
            self.in_table += 1
        elif tag in ("td", "th"):
            self.in_cell = True
            self.parts.append(" | ")
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style"):
            self.in_script = max(0, self.in_script - 1)
        elif tag == "table":
            self.in_table = max(0, self.in_table - 1)
            self.parts.append("\n")
        elif tag in ("td", "th"):
            self.in_cell = False
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.in_script:
            return
        self.parts.append(data)


def html_to_text(html: str | bytes) -> str:
    if isinstance(html, bytes):
        html = html.decode("utf-8", "ignore")
    parser = _Extractor()
    parser.feed(html)
    text = "".join(parser.parts)
    text = re.sub(r"[ \t\u00a0]+", " ", text)
    text = re.sub(r" ?\| ?", " | ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
