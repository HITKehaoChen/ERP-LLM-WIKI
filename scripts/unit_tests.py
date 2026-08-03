"""Unit tests for pure logic (tokenizer, markdown renderer, knowledge layer).

Run: python scripts/unit_tests.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
sys.path.insert(0, str(ROOT / "scripts"))

import knowledge  # noqa: E402
import markdown_render  # noqa: E402


class TestTokens(unittest.TestCase):
    def test_latin_words(self):
        self.assertIn("order", knowledge.tokens("Order Management"))

    def test_cjk_bigrams(self):
        toks = knowledge.tokens("OM模块的业务流程")
        self.assertIn("业务", toks)
        self.assertIn("流程", toks)

    def test_mixed(self):
        toks = knowledge.tokens("WIP 倒冲 backflush")
        self.assertIn("wip", toks)
        self.assertIn("backflush", toks)
        self.assertIn("倒冲", toks)


class TestSearch(unittest.TestCase):
    def test_cjk_query_finds_om_page(self):
        results = knowledge.search("OM模块的业务流程是什么样子的", raw=False, top=5)
        paths = [r["path"] for r in results]
        self.assertTrue(paths)
        self.assertTrue(any("om-workflow" in p or "order-management" in p for p in paths))

    def test_raw_search(self):
        results = knowledge.search("Invoice Interface", raw=True, top=3)
        self.assertTrue(results)


class TestMarkdown(unittest.TestCase):
    def test_headings_and_lists(self):
        html = markdown_render.render("# 标题\n\n- a\n- b\n\n| x | y |\n|---|---|\n| 1 | 2 |")
        self.assertIn("<h1>标题</h1>", html)
        self.assertIn("<li>a</li>", html)
        self.assertIn("<table>", html)
        self.assertIn("<td>1</td>", html)

    def test_escape(self):
        html = markdown_render.render("<script>alert(1)</script>")
        self.assertNotIn("<script>", html)

    def test_links(self):
        html = markdown_render.render("[x](https://example.com)")
        self.assertIn('href="https://example.com"', html)

    def test_javascript_url_blocked(self):
        html = markdown_render.render("[x](javascript:alert(1))")
        self.assertNotIn("javascript:", html)
        html2 = markdown_render.render("![img](data:text/html,<script>1</script>)")
        self.assertNotIn("data:", html2)


class TestKnowledge(unittest.TestCase):
    def test_page_path_traversal_rejected(self):
        self.assertIsNone(knowledge.page_markdown("../../Windows/win.ini"))
        self.assertIsNone(knowledge.page_markdown("wiki/../secret.md"))

    def test_page_load(self):
        md = knowledge.page_markdown("wiki/concepts/order-lifecycle-and-status.md")
        self.assertIsNotNone(md)
        self.assertIn("Booked", md)

    def test_graph(self):
        g = knowledge.build_graph()
        self.assertGreater(len(g["nodes"]), 50)
        self.assertGreater(len(g["links"]), 50)
        ids = {n["id"] for n in g["nodes"]}
        for l in g["links"]:
            self.assertIn(l["source"], ids)
            self.assertIn(l["target"], ids)
            self.assertNotEqual(l["source"], l["target"])

    def test_ingest_dry_run(self):
        r = knowledge.ingest("UT-测试", "内容", "https://example.com", dry_run=True)
        self.assertTrue(r["dry_run"])
        self.assertTrue(r["path"].startswith("sources/inbox/"))

    def test_ingest_too_large(self):
        with self.assertRaises(ValueError):
            knowledge.ingest("UT-大", "x" * 200_001, dry_run=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
