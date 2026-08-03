# AGENTS.md — Oracle EBS R12.2 LLM Wiki Schema

本文件是这个知识库的 **schema 层**（Karpathy “LLM Wiki” 模式：raw 原始素材 → wiki 编译层 → schema 配置层）。
任何 Codex / Claude / 其他 LLM 会话在读取或修改本知识库之前，必须先完整阅读本文件，并遵守其中的约定。

## 1. 知识库定位与边界

- 定位：**Oracle EBS R12.2 标品文档知识库**，以官方公开文档为主，逐步编译成相互链接的 Markdown Wiki。
- 不要把它命名为或当作“Oracle EBS 全部业务逻辑库”：没有 ERP / MOS 权限时，源码级逻辑、补丁差异、当前实例行为没有证据，必须**留白**，不得用推断冒充事实。
- 知识分层：
  - `T1 官方文档原文`：直接引用官方文档章节，必须给出来源页与章节名（最好带 URL 锚点）。
  - `T2 文档归纳`：由文档章节结构/内容归纳出的概要，允许，但要标为归纳。
  - `T3 推断/假设`：未经文档或实例验证的推断、记忆、猜测，必须用 `> ⚠ 未验证` 块标注，并列入页面的 Open Questions。
  - `T4 实例验证`：只有获得只读 ERP/eTRM/MOS 权限后才能使用；当前一律不标。

## 2. 三层架构

```text
ERP/
├── AGENTS.md              # schema 层：本文件
├── README.md              # 人类入口
├── llms.txt               # LLM 入口
├── sources/               # raw 层：不可变，只读
│   ├── catalog/           #   官方书单/导航分类的机器可读索引（脚本生成）
│   └── docs/<part>/       #   官方页面原始快照：toc.html、title.html 或 PDF
├── wiki/                  # 编译层：LLM 全权维护
│   ├── index.md           #   内容索引（每次变更后更新）
│   ├── log.md             #   时间线日志（append-only）
│   ├── overview.md        #   知识库总览与综合
│   ├── domains/           #   业务域页：wip / inventory / order-management / intercompany …
│   ├── entities/          #   业务对象页：WIP Job、Sales Order、Item …
│   ├── processes/         #   端到端流程页
│   ├── concepts/          #   概念页：MOAC、成本方法、SLA …
│   ├── sources/           #   每份重点文档一页（脚本生成起点 + LLM 修订）
│   └── coverage/          #   覆盖率与缺口报告
└── scripts/               # 抓取与构建工具
```

## 3. 页面规范

### 3.1 命名

- 文件名一律小写连字符，如 `work-in-process.md`、`sales-order.md`。
- 每个主题一个文件；不要重复建同义页面。

### 3.2 Frontmatter

```yaml
---
title: "Work in Process（WIP）"
type: domain            # domain | entity | process | concept | source | coverage | index | overview
status: draft           # draft | stable
verified: doc-only      # doc-only | instance-verified | needs-verification
sources: [e48905, e48954, e48829]
updated: 2026-08-03
---
```

- `verified` 与 `status` 分开：`verified` 描述证据等级，`status` 描述页面完成度。
- 页面主体中每个关键论断尽量携带证据链接，格式：
  `[e48905 · “WIP Accounting Classes”](wiki/sources/e48905.md)`，必要时追加章节标题与 URL 锚点。

### 3.3 链接

- 用 Markdown 链接把页面织成图：领域页 → 实体页 → 流程页 → 来源页，禁止孤岛。
- 相对路径以 `wiki/` 为基准；raw 快照用 `../../sources/docs/<part>/toc.html`。

### 3.4 矛盾处理

- 新来源与旧页面冲突时，**不得静默覆盖**。在旧页相关位置加：

  ```markdown
  > [!contradiction] 矛盾
  > 旧说法（来源 A）：……
  > 新说法（来源 B）：……
  > 结论/待验证：……
  ```

  并在 `log.md` 记录这次矛盾。

### 3.5 留白规则

- 文档没有写的内容（表名、字段、触发条件、真实调用链）明确写“当前无证据”，列入 Open Questions。
- 禁止把“Oracle 可能这样做”写成“Oracle 这样做”。

## 4. 操作流程

### 4.1 Ingest（摄入新素材）

1. 新素材放入 `sources/`（官方文档用 `scripts/fetch_priority_docs.py`，书单用 `scripts/fetch_ebs_catalog.py`）。
2. 通读素材，提取关键信息。
3. 更新或新建相关页面（领域/实体/流程/概念/来源页），并更新 `wiki/index.md`。
4. 追加 `wiki/log.md` 一条：
   `## [2026-08-03] ingest | <文档名或素材名>`
5. 若产生矛盾，按 3.4 处理。

### 4.2 Query（查询）

1. 先读 `wiki/index.md`，再钻取相关页面；必要时才回到 raw 层核对原文。
2. 需要定位知识时先运行 `python scripts/search_wiki.py "<问题>"`（加 `--raw` 可同时搜官方章节原始正文；`--build-index` 生成 `wiki/search-index.json` 供网页端使用）。
2. 回答必须给出引用（来源页 + 章节），并区分 T1/T2/T3。
3. 有价值的回答（对比、分析、新发现）**回写成新页面**并记 log，不要让它只存在于聊天记录里。

### 4.3 Lint（健康检查）

1. 检查：断链、孤儿页、陈旧声明、缺失交叉引用、矛盾块、`index.md`/`log.md` 是否过期、coverage 是否过期。
2. 运行 `python scripts/lint_wiki.py`，修复它报告的问题。
3. 记录 `## [YYYY-MM-DD] lint | <发现与修复摘要>`。

## 5. 数据来源与刷新

- `scripts/fetch_ebs_catalog.py`：抓 Oracle “Current Booklist” 与 12 个产品导航页 → `sources/catalog/`。
- `scripts/fetch_priority_docs.py`：抓重点文档 TOC/Title/PDF 快照 → `sources/docs/` + `sources/catalog/priority_docs.json`。
- `scripts/build_wiki_sources.py`：由 catalog 生成 `wiki/sources/` 页面（重新运行会覆盖，LLM 的附加修订请放在页面中“LLM 修订”区，脚本生成区不要手改）。
- 抓取时间记录在 `sources/catalog/*.json` 的 `fetched_at`；判断文档新旧先看这个字段和 Part Number 后缀。

## 6. 当前重点域（2026-08-03）

1. WIP（任务/工序/物料/成本）
2. Inventory（物料/组织/事务/批次序列）
3. Order Management（销售订单闭环）
4. Intercompany / 关联交易（AGIS 及 GL/AR/AP/SLA 链路）

这四块先做深，其余域只做目录级覆盖。
