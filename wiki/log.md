# log.md — 时间线日志

> 追加式记录；条目以 `## [YYYY-MM-DD] 类型 | 标题` 开头，可用 `grep "^## \[" log.md | tail` 查看最近记录。

## [2026-08-03] build | 初始化知识库骨架

- 按 Karpathy LLM Wiki 模式建立 `sources/`（raw）、`wiki/`（编译层）、`AGENTS.md`（schema）三层结构。
- 创建 README、llms.txt、wiki/index.md、wiki/log.md、wiki/overview.md、wiki/coverage/report.md。

## [2026-08-03] ingest | Oracle EBS R12.2 Current Booklist（393 本）

- 抓取官方 Booklist 与 12 个产品导航页，生成 `sources/catalog/ebs_r122_booklist.json/.csv` 与 `ebs_r122_areas.json`。
- 393 本全部有 Part Number；367 本映射到产品域；13 本为失效旧路径（legacy_broken）。

## [2026-08-03] ingest | 63 份重点文档快照（WIP/INV/OM/关联交易/基础）

- 抓取 63 份重点文档的 toc.html/title.html 或 PDF 快照到 `sources/docs/`，解析章节树到 `sources/catalog/priority_docs.json`。
- 生成 63 份来源页 + `wiki/sources/index.md`。
- 已知问题：e48763（Payables Reference Guide）HTML 路径已失效，仅 PDF 可用。

## [2026-08-03] lint | 首次健康检查

- 修复 catalog 脚本中 13 本旧路径文档的 Part Number 解析缺失。
- 修复 priority 脚本中 JSON 落盘代码被错误嵌入函数的问题。
- 修复 AGENTS.md 中证据链接示例的路径（sources → wiki/sources）。
- `python scripts/lint_wiki.py` 通过：84 个文件，无断链、无孤儿页、无缺失 frontmatter。

## [2026-08-04] ingest | e48843 销售订单生命周期正文（T1）

- 抓取 OM User's Guide 全部 24 个章节 HTML 到 `sources/docs/e48843/chapters/`。
- 逐章提取：订单头/行全部状态清单、Booking（手动/延迟）、Fulfillment（FULFILL 同步点）、Invoice Interface 规则与 Flow Status 查找码、取消/关闭/Holds 规则。
- 新页：[销售订单生命周期与状态机（T1）](concepts/order-lifecycle-and-status.md)；sales-order 实体页升级为 stable。

## [2026-08-04] ingest | e48905 WIP 正文快照

- 抓取 WIP User's Guide 全部 27 个章节 HTML 到 `sources/docs/e48905/chapters/`，正文提取待整理。

## [2026-08-04] ingest | WIP 状态机正文（T1）

- 从 e48905 第 “Job and Repetitive Schedule Statuses” 章提取：离散任务/重复性计划全部状态定义、官方状态转换矩阵、按状态的事务控制、ECO/计划/报表控制。
- 新页：[WIP 任务与重复性计划状态机（T1）](concepts/wip-job-status-machine.md)；wip-job 实体页升级为 stable。

## [2026-08-04] ingest | Inventory 账户体系正文（T1）

- 抓取 e48820 全部 27 个章节 HTML；提取估价账户、其他账户、PPV/IPV 公式、子库科目、组织间转移账户。
- 新页：[Inventory 账户设置与科目推导（T1）](concepts/inventory-accounting.md)。

## [2026-08-04] ingest | WIP 会计类别与 SLA 成本事件（T1）

- 抓取 e48829（25 章）、e48771（15 章）、e48781（6 章）正文 HTML。
- 提取 WIP Valuation/Variance 账户行为、SLA 成本事件模型（WIP/材料/接收事件实体与 JLT 条件）。
- 新页：[SLA 成本事件模型（T1）](concepts/sla-costing-events.md)。

## [2026-08-04] tooling | 本地检索工具

- 新增 `scripts/search_wiki.py`：wiki 全文检索（标题/标签/标题行/正文加权），`--raw` 可检索官方章节原始正文，`--build-index` 生成 `wiki/search-index.json`。
- AGENTS.md Query 流程与 llms.txt 已登记检索用法。

## [2026-08-04] ingest | AGIS 关联交易正文（T1）

- 从 e48781 提取：Outbound/Inbound 流程、批号编号机制、工作流通知、转 GL（Online/Batch + Journal Import/Posting）、转 AR/AP、撤回/冲销、Open Interface 表关键字段与批约束。
- 新页：[AGIS 关联交易处理链路（T1）](concepts/intercompany-processing-t1.md)。

## [2026-08-04] lint | T1 摄入后健康检查

- 重建 `wiki/search-index.json`（86 页）。
- `python scripts/lint_wiki.py` 通过：89 个文件，无断链、无孤儿页、无缺失 frontmatter。

## [2026-08-04] ingest | e48842/e48847 正文（T1）

- 抓取 e48842 全部 32 章、e48847 全部 19 章 HTML。
- 提取 OM 交易类型（Order/Line、单据序列、开票默认顺序、Enforce List Price、默认规则框架、处理约束）与 Shipping 交付行状态/Pick Release/Ship Confirm/LPN 规则。
- 新页：[OM 交易类型与默认规则（T1）](concepts/om-transaction-types-defaulting.md)、[Shipping 发运状态与流程（T1）](concepts/shipping-statuses-and-processes.md)。

## [2026-08-04] build | LLM Wiki 网页界面（本地 Web 应用）

- 新增 `app/`（零依赖：stdlib HTTP 服务 + 自研 Markdown 渲染）与 `scripts/run_app.py`、`scripts/test_app.py`。
- API：health / search / pages / page / raw / ask（LLM 或本地降级）/ ingest / render-md。
- 前端三页签：浏览与检索、提问（可复制 Prompt 交给 Codex）、补充知识（写入 `sources/inbox/` + log）。
- `scripts/test_app.py` 冒烟测试全部通过；`/` 与静态资源 200。

## [2026-08-04] lint | 网页与 T1 摄入后复查

- 重建 raw index（175 章节）与 wiki index（88 页）。
- `python scripts/lint_wiki.py` 通过：91 个文件，无断链、无孤儿页、无缺失 frontmatter。

## [2026-08-04] ingest | WIP 物料控制与完工正文（T1）

- 从 e48905 “Material Control” 章提取：发料/退料、Backflush 触发与规则、反向倒冲、完工事务类型与行为、供应子库补货、负库存规则。
- 新页：[WIP 物料控制与完工（T1）](concepts/wip-material-control-and-completions.md)。

## [2026-08-04] ingest | Intercompany Invoicing / CIC 正文（T1）

- 从 e48820 “Intercompany Invoicing” 与 e48829 “Complex Intercompany Invoicing” 提取：业务流程、前置设置、Profile、交易流（Shipping/Procuring）、会计分布与币种规则、OU 链分录示例。
- 新页：[Intercompany Invoicing 与复杂关联交易（CIC）（T1）](concepts/intercompany-invoicing-t1.md)。

## [2026-08-04] build | 网页新增待摄入箱

- `GET /api/inbox` + 前端“待摄入箱”列表：展示 `sources/inbox/` 中待摄入条目（标题/状态/来源）。
- SLA 页补充 ALT/RALT 条件表与 Legend。

## [2026-08-04] ingest | 事务规则与账户推导补全（T1）

- e48820 Transaction Setup：事务类型=来源类型+动作、种子类型表、原因、账户别名、处理模式/管理器 → [Inventory 事务类型与处理模式（T1）](concepts/inventory-transaction-types.md)。
- e48771 AMB：八步流程、交易/会计科目表、映射集、业务流（Same/Prior/None）示例 → [SLA AMB 账户推导规则（T1）](concepts/sla-amb-account-derivation.md)。
- e48905 Supply Types 并入 [WIP 物料控制与完工（T1）](concepts/wip-material-control-and-completions.md)。
- e48844（12 章全文）：种子流程/子流程清单、CTO/ISO 流程、后台引擎与验证 → [OM 工作流与种子流程（T1）](concepts/om-workflow-t1.md)。

## [2026-08-04] lint | 补全后复查

- raw 索引 187 章、wiki 索引 93 页；`lint_wiki.py` 通过（96 文件）；`test_app.py` 全部通过。

## [2026-08-04] ingest | 细化补齐（T1）

- CIC 页补 OU2/OU1 完整分录（Receiving/Deliver/Shipping/AR 各步）。
- AMB 页补 Account Derivation Rules 窗口字段（Output/Value Type、Priority、科目表配置、段/值集规则、示例）。
- 新页 [OM 关键 Profile 选项（T1）](concepts/om-profile-options-t1.md)。
- 新页 [成本管理事务会计分录（T1）](concepts/cost-management-transactions-t1.md)（标准成本分销/制造、平均成本库存）。
- OM Workflow 页补 6 个关键子流程的活动表（Book/Close/Schedule/Ship/Invoice Interface/Enter）。

## [2026-08-04] verify | 端到端问答验证

- 启动本地服务，`/api/ask` 实测“订单行何时进入 Awaiting Invoice Interface - On Hold”，返回 13 条引用，首位命中 [销售订单生命周期与状态机（T1）](concepts/order-lifecycle-and-status.md)（得分 119）。
- `lint_wiki.py` 通过（98 文件）；`test_app.py` 全部通过；wiki 索引 95 页。

## [2026-08-04] ingest | 可选增强项（T1）

- OM Workflow 页补主流程活动：Order/Line Flow - Generic、Booking Approval、Header Level Invoice、Performance 流程。
- 成本页补：FIFO/LIFO 层成本事务（含层建立规则）、项目制造成本（成本组/Project Cost Collector/分录）、周期成本处理顺序与规则。
- OM Profile 页补 103 个 Profile 代码清单（e48842 正文）。

## [2026-08-04] config | 接入 DeepSeek LLM

- `app/llm_config.json`（gitignored）配置 DeepSeek（base_url=https://api.deepseek.com，model=deepseek-v4-flash）。
- `llm.py` 支持本地配置文件 + 环境变量覆盖；`/api/health` 显示实际模型。
- 实测 `/api/ask` 返回 `mode=llm`，DeepSeek 正确区分 T1 原文与未验证推断。

## [2026-08-04] fix | 中文检索与问答上下文

- 问题“OM模块的业务流程是什么样子的”此前“可参考资料”为空：原因是中国查询被当成一个 token，全文检索零命中。
- 修复：CJK 按字符二元组+单字分词（`app/knowledge.py`、`scripts/search_wiki.py`），同一问题现命中 95 条，OM 工作流页排第一。
- 问答增强：`/api/ask` 把 top 命中页面的正文摘录（按查询词定位 ±上下文）并入 Prompt，模型可基于 T1 知识回答并引用来源。
- 新增中文检索回归测试 `search-cjk`。

## [2026-08-04] ingest | 用户补充资料

- O2C 培训 PDF（19 页，含 OE/WSH/RA/AR/GL 表字段与示例 SQL）：归档到 `sources/docs/o2c/`，知识页整理中。
- Oracle R12.1 数据模型附录链接 → 确认本地已有 R12.2 等价章节，新增 [OM 数据模型概览（T1）](concepts/om-data-model-t1.md)。
- 博客 Open Interfaces 综述：保存 HTML/文本快照到 `sources/docs/community/`，新增 [OM Open Interfaces 与 API（T2）](concepts/om-open-interfaces.md)。
- O2C PDF 结构化：新增 [Order-to-Cash 表级流程（T2 社区资料）](concepts/order-to-cash-with-tables.md)，sales-order-to-cash 页挂接。
- YouTube 字幕：新增 `scripts/fetch_youtube_transcript.py`，成功抓取 2mMtLycHK-4 英文字幕（191 段）到 `sources/docs/community/youtube/`，摘要并入 O2C 页。

## [2026-08-04] ingest | 补充 report.md 缺口

- 各工作流变体活动表（OM Workflow 页第 9 节）、制造事务分录（资源/外协/间接费/报废/完工/关闭/期间关闭，成本页 3.4）、e48842 Profile 默认值（154 行 CSV + 页面附录 2）。
- 13 本 legacy 文档 PDF 全部核验可用并下载归档；catalog 脚本补 PDF 兜底链接；report.md 同步状态。

## [2026-08-04] frontend | 现代化重构 + 知识图谱

- 重写前端：响应式布局、明暗主题、全局搜索、对话式问答、待摄入箱表单。
- 新增 `GET /api/graph` 与 Canvas 力导向知识图谱（拖拽/缩放/点击跳转）。

## [2026-08-04] testing | 测试基线

- 新增 `scripts/unit_tests.py`、`scripts/e2e_test.py`、`scripts/run_checks.py`；一键运行 UT + 冒烟 + 真实启动 E2E + lint，全部通过。

## [2026-08-04] review | 独立视角审查与修复

- 子代理消息投递在本环境不可用（创建/跟进消息均未进入子代理上下文），改为独立视角结构化自审。
- 修复：Markdown 链接 scheme 白名单（拦截 javascript:/data:）、Canvas 图谱标签颜色改用计算样式、全局搜索自动切页签、ingest 内容 200KB 上限。
- 新增对应 UT/E2E 用例；`run_checks.py` 全部通过（UT 14 项）。























