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
- **LLM 配置**：也可以直接编辑 `app/llm_config.json`（已加入 .gitignore，不会提交密钥）：
  `{"base_url": "https://api.deepseek.com", "api_key": "sk-...", "model": "deepseek-v4-flash"}`。
  环境变量 `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL` 优先级更高；修改后重启服务生效。
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
python scripts/run_checks.py
```

覆盖：单元测试（分词/渲染/路径安全/图谱）、进程内冒烟、真实启动进程的 E2E（每个功能逐项验证）、wiki lint。

## 界面

- **检索**：支持中文（CJK 二元组分词）；左侧结果、右侧页面阅读；可含官方章节原文检索。
- **知识图谱**：`GET /api/graph` 返回节点与交叉引用边；前端 Canvas 力导向图（拖拽/缩放/点击打开）。
- **提问**：对话式；回答带引用，可复制 Prompt 给 Codex。
- **补充知识**：写入待摄入箱并列出。
