# LLM Wiki Web UI

一个零依赖（Python 标准库）的本地网页界面，用于浏览/检索 Oracle EBS LLM Wiki、向知识库提问、补充知识。

## 启动

```powershell
python scripts/run_app.py            # 打开 http://127.0.0.1:8000
python scripts/run_app.py --port 9000
```

## 功能

- **浏览与检索**：全文检索 wiki 页面；勾选“同时搜官方章节正文”可检索 `sources/docs/*/chapters/` 的原始 HTML 文本。
- **提问**：本地检索 top-k 片段后组装上下文；配置了 `OPENAI_API_KEY`（可用 `OPENAI_BASE_URL` 指向公司 OpenAI 兼容 endpoint、`OPENAI_MODEL` 指定模型）时由 LLM 生成带引用的答案；未配置时自动降级为本地检索结果。可一键复制“交给 Codex 的 Prompt”。
- **补充知识**：表单写入 `sources/inbox/`（frontmatter 标记 `type: inbox`、`status: pending-ingest`），并追加 `wiki/log.md`，等待 Codex 正式摄入。

## API

- `GET /api/health` — 状态（页面数、章节数、LLM 是否配置）
- `GET /api/search?q=…&raw=1&top=8` — 检索
- `GET /api/pages` — wiki 页面清单
- `GET /api/page?path=wiki/…` — 页面 markdown + 渲染 HTML
- `GET /api/raw?path=sources/docs/…` — 原始章节文本
- `POST /api/ask` `{question, raw}` — 提问（LLM 或本地模式）
- `POST /api/ingest` `{title, content, source_url}` — 补充知识
- `POST /api/render-md` `{md}` — Markdown 渲染

## 测试

```powershell
python scripts/test_app.py
```

测试覆盖：health、检索、页面渲染、本地问答、补充知识（dry-run + 真实写入后清理）、Markdown 渲染。
