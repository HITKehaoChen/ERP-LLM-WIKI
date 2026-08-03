"""Minimal, dependency-free Markdown -> HTML renderer for the LLM Wiki UI."""

from __future__ import annotations

import html
import re


def _inline(text: str) -> str:
    text = html.escape(text, quote=False)
    # images (keep as link to the target)
    text = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        lambda m: f'<a href="{_attr(_safe_url(m.group(2)))}">图片: {m.group(1) or m.group(2)}</a>',
        text,
    )
    # links
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{_attr(_safe_url(m.group(2)))}" target="_blank" rel="noopener">{m.group(1)}</a>',
        text,
    )
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def _attr(url: str) -> str:
    return html.escape(url, quote=True)


def _safe_url(url: str) -> str:
    """Only allow safe URL schemes; block javascript:/vbscript:/data: etc."""
    stripped = url.strip()
    low = stripped.lower()
    if ":" in low.split("/", 1)[0] and not low.startswith(
        ("http://", "https://", "mailto:", "#", "/", "./", "../")
    ):
        return "#"
    return stripped


def render(md: str) -> str:
    """Render the markdown subset used by the wiki (headings, code, tables,
    lists, blockquotes, links)."""
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)
    in_fence = False

    while i < n:
        line = lines[i]

        # fenced code / mermaid
        if line.lstrip().startswith("```"):
            if in_fence:
                out.append("</code></pre>")
                in_fence = False
            else:
                lang = line.lstrip()[3:].strip()
                out.append(f'<pre><code class="language-{html.escape(lang)}">')
                in_fence = True
            i += 1
            continue
        if in_fence:
            out.append(html.escape(line))
            i += 1
            continue

        # heading
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # blockquote
        if line.lstrip().startswith(">"):
            quote_lines = []
            while i < n and lines[i].lstrip().startswith(">"):
                quote_lines.append(lines[i].lstrip()[1:].strip())
                i += 1
            out.append("<blockquote>" + "<br>".join(_inline(q) for q in quote_lines) + "</blockquote>")
            continue

        # table: header row followed by separator row
        if line.strip().startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:\-|]+\|\s*$", lines[i + 1]):
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = ["<table><thead><tr>"]
            t += [f"<th>{_inline(c)}</th>" for c in header]
            t.append("</tr></thead><tbody>")
            for row in rows:
                cells = row + [""] * (len(header) - len(row))
                t.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in cells[: len(header)]) + "</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            continue

        # unordered list
        if re.match(r"^\s*[-*]\s+", line):
            items = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(_inline(re.sub(r"^\s*[-*]\s+", "", lines[i])))
                i += 1
            out.append("<ul>" + "".join(f"<li>{it}</li>" for it in items) + "</ul>")
            continue

        # ordered list
        if re.match(r"^\s*\d+\.\s+", line):
            items = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(_inline(re.sub(r"^\s*\d+\.\s+", "", lines[i])))
                i += 1
            out.append("<ol>" + "".join(f"<li>{it}</li>" for it in items) + "</ol>")
            continue

        # horizontal rule
        if re.match(r"^\s*---+\s*$", line) or re.match(r"^\s*\*\*\*+\s*$", line):
            out.append("<hr>")
            i += 1
            continue

        # blank line
        if not line.strip():
            i += 1
            continue

        # paragraph (gather until blank)
        para = [line]
        i += 1
        while i < n and lines[i].strip() and not re.match(r"^(#{1,6}\s|```|>\s?|\s*[-*]\s+|\s*\d+\.\s+)", lines[i]):
            para.append(lines[i])
            i += 1
        out.append("<p>" + _inline(" ".join(p.strip() for p in para)) + "</p>")

    return "\n".join(out)
