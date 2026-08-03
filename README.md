# Oracle EBS R12.2 LLM Wiki

一个按 [Karpathy LLM Wiki 模式](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 构建的 Oracle EBS R12.2 知识库：LLM 持续把官方文档编译成结构化的 Markdown Wiki，而不是每次查询都重新 RAG。

## 当前状态（2026-08-04）

- 已建立 Oracle EBS R12.2 官方文档**全集索引**：393 本书，367 本映射到产品域（HCM/财务/SCM/CRM/技术等 12 个导航分类）。
- 已抓取 **63 份重点文档**的原始快照与章节树，聚焦 WIP、Inventory、Order Management、关联交易/财务、基础技术。
- 已抓取 **175 个官方章节正文**，并把销售订单状态机、WIP 状态机、Inventory 账户推导、SLA 成本事件、AGIS 处理链路、OM 交易类型/默认规则、Shipping 发运状态升级为 **T1 官方原文级知识**。
- 已搭建三层结构：`sources/`（原始素材，不可变）、`wiki/`（编译层）、`AGENTS.md`（schema）。
- 已提供本地网页界面（浏览/检索/提问/补充知识）：`python scripts/run_app.py`，详见 [app/README.md](app/README.md)。
- 已知缺口：13 本书单链接失效；Payables Reference Guide 仅 PDF；MOS、eTRM 全量、实例只读权限未获得（详见 [覆盖率报告](wiki/coverage/report.md)）。

## 快速开始

1. 用 Obsidian 打开本目录，`wiki/index.md` 是内容入口。
2. 让 Codex 回答业务问题时，先读 `wiki/index.md`，再按引用回溯到 `wiki/sources/` 和官方链接。
3. 新资料入库走 `AGENTS.md` 的 Ingest 流程。

## 网页界面（LLM Wiki UI）

```powershell
python scripts/run_app.py
```

打开 http://127.0.0.1:8000 即可浏览/检索知识、向知识库提问（可配置 `OPENAI_API_KEY` 启用 LLM 回答，未配置时自动降级为本地检索）、以及补充新知识到待摄入箱。详见 [app/README.md](app/README.md)。

界面包含四个页签：**检索**（搜索结果+页面阅读）、**知识图谱**（力导向图，节点=知识页、边=交叉引用，可拖拽/缩放/点击跳转）、**提问**（对话式问答）、**补充知识**（待摄入箱管理）。支持明暗主题与移动端自适应。

## 测试基线

每次修改后运行（UT + 进程内冒烟 + 真实启动 E2E + wiki lint）：

```powershell
python scripts/run_checks.py
```

- `scripts/unit_tests.py`：分词、检索、Markdown 渲染、路径安全、图谱、ingest dry-run 等纯逻辑测试。
- `scripts/test_app.py`：进程内 API 冒烟测试。
- `scripts/e2e_test.py`：以真实子进程启动应用，逐项验证首页/静态资源/检索/页面/原始章节/图谱/问答/补充知识/404。
- `scripts/lint_wiki.py`：wiki 断链/孤儿页/frontmatter 检查。

## 目录速览

- [wiki/index.md](wiki/index.md) — 内容索引
- [wiki/overview.md](wiki/overview.md) — 知识库总览
- [wiki/coverage/report.md](wiki/coverage/report.md) — 文档覆盖率与缺口
- [sources/catalog/ebs_r122_booklist.csv](sources/catalog/ebs_r122_booklist.csv) — 全集书单（393 本）
- [AGENTS.md](AGENTS.md) — LLM 维护约定

## 重要边界

本知识库是“标品文档知识库”，不是“全部业务逻辑库”。没有 ERP/MOS 权限时，源码级逻辑、当前补丁差异、企业实例的真实行为均未验证，页面中一律标注留白。
