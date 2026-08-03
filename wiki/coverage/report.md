---
title: 文档覆盖率与缺口报告
type: coverage
status: stable
updated: 2026-08-04
---

# Oracle EBS R12.2 文档覆盖率报告

## 1. 全集索引

官方 [Current Booklist](https://docs.oracle.com/cd/E26401_01/nav/portal_booklist.htm) 抓取于 2026-08-03：

| 指标 | 数值 |
| --- | --- |
| 书单总数 | 393 |
| 有 Part Number | 393 |
| 已映射产品导航域 | 367 |
| 旧路径失效（legacy_broken） | 13 |

按产品导航域分布（367 本中，含跨域重复计数）：

| 域 | 文档数 |
| --- | --- |
| HCM | 78 |
| Financials | 52 |
| SCM | 50 |
| CRM | 42 |
| Technology | 33 |
| Service | 31 |
| VCP | 31 |
| Procurement | 19 |
| Projects / MDM | 各 11 |
| VCE（含 Inventory） | 11 |
| G-Invoicing | 6 |

## 2. 重点文档快照（63 份）

| 业务域 | 份数 | 覆盖内容 |
| --- | --- | --- |
| WIP / 离散制造 | 13 | WIP、BOM、成本、MES、SFM、Flow、OSM、Quality、MOC |
| Inventory / VCE | 10 | Inventory、WMS、MSCA、LCM、Yard、Consigned、Movement Stats |
| Order Management | 9 | OM、Shipping、Advanced Pricing、CTO、Release Mgmt |
| 关联交易 / 财务 | 17 | AGIS、Financials、GL、AP、AR、SLA、E-Business Tax、Payments |
| 基础 / 技术 | 14 | Concepts、Multi-Org、Developer、Flexfields、Workflow、SOA Gateway、eTRM、Install/Upgrade |

快照状态：62 份 HTML 可用；1 份（e48763 Payables Reference Guide）HTML 已失效、PDF 已保存。

### 2.1 正文逐章抓取与 T1 摄入（截至 2026-08-04）

已抓取整章正文 HTML 的文档（共 187 个章节文件）：

| 文档 | 章节文件数 | T1 页面 |
| --- | --- | --- |
| e48843 Order Management User's Guide | 24 | [销售订单生命周期与状态机](../concepts/order-lifecycle-and-status.md) |
| e48905 Work in Process User's Guide | 27 | [WIP 任务与重复性计划状态机](../concepts/wip-job-status-machine.md) |
| e48820 Inventory User's Guide | 27 | [Inventory 账户设置与科目推导](../concepts/inventory-accounting.md) |
| e48829 Cost Management User's Guide | 25 | [SLA 成本事件模型](../concepts/sla-costing-events.md) |
| e48771 Subledger Accounting Implementation | 15 | [SLA AMB 账户推导规则](../concepts/sla-amb-account-derivation.md) |
| e48781 Advanced Global Intercompany System | 6 | [AGIS 关联交易处理链路](../concepts/intercompany-processing-t1.md) |
| e48842 Order Management Implementation Manual | 32 | [OM 交易类型与默认规则](../concepts/om-transaction-types-defaulting.md) |
| e48847 Shipping Execution User's Guide | 19 | [Shipping 发运状态与流程](../concepts/shipping-statuses-and-processes.md) |
| e48844 OM Using Workflow | 12 | [OM 工作流与种子流程](../concepts/om-workflow-t1.md) |

已 T1 化的知识类型：销售订单状态清单与 Booking/Fulfillment/Invoice/Cancel/Close 规则；OM 交易类型/单据序列/默认规则/处理约束；Shipping 交付行状态与 Pick/Ship Confirm 规则；WIP 任务状态定义与官方转换矩阵；Inventory 估价/其他/子库/组织间转移账户；SLA 成本事件模型（WIP/材料/接收）；AGIS 批次/审批/转 GL/AR-AP 与接口表。

2026-08-04 补充 T1 页：[WIP 物料控制与完工](../concepts/wip-material-control-and-completions.md)（倒冲触发/规则/完工事务类型）、[Intercompany Invoicing 与 CIC](../concepts/intercompany-invoicing-t1.md)（交易流/会计分布/OU 链分录）、SLA 页补充 ALT/RALT 条件表。

再补：[Inventory 事务类型与处理模式](../concepts/inventory-transaction-types.md)（来源类型+动作、账户别名、处理模式）、[SLA AMB 账户推导规则](../concepts/sla-amb-account-derivation.md)（科目表/映射集/业务流）、[OM 工作流与种子流程](../concepts/om-workflow-t1.md)（种子流程/子流程清单）；WIP 物料页并入 Supply Types。

最终细化：[成本管理事务会计分录](../concepts/cost-management-transactions-t1.md)（标准成本分销/制造、平均成本库存默认分录）、[OM 关键 Profile 选项](../concepts/om-profile-options-t1.md)；CIC 页补 OU2/OU1 完整分录；AMB 页补 Account Derivation Rules 窗口字段；OM Workflow 页补 6 个关键子流程活动表。

### 2.2 T1 覆盖结论

截至 2026-08-04，目标范围内的核心知识已 T1 化并有官方原文证据：

- 状态机：销售订单（头/行状态、Booking/Fulfillment/Invoice/Cancel/Close）、WIP（状态定义+转换矩阵）、Shipping（交付行状态机）。
- 事务规则：OM 交易类型/默认规则/处理约束、OM 工作流与种子流程、WIP 物料控制/倒冲/完工/Supply Types、Inventory 事务类型与处理模式、AGIS 批次/审批/转出。
- 账户推导：Inventory 账户体系、WIP 估价/差异账户、SLA 成本事件+ALT/RALT 条件、AMB 映射集/账户推导规则/业务流、成本管理默认分录、Intercompany Invoicing/CIC 会计分布与 OU 链分录。

剩余细化项（可选增强，不阻塞使用）：全部种子工作流活动的逐条明细、FIFO/LIFO/项目制造/周期成本分录全文、e48842 完整 Profile 清单与默认值、eTRM 表字段、MOS/实例验证。

2026-08-04 再补：OM 主流程活动表（Generic/Booking Approval/Header Invoice/Performance）、层成本/项目成本/周期成本处理与分录、e48842 Profile 代码清单（103 个）。剩余仅：各工作流变体逐条活动明细、制造事务分录逐条摘录、Profile 默认值表、以及需要权限的 eTRM/MOS/实例验证。

**可选增强（见 2.2）**：
1. ✅ 各工作流变体的逐条活动明细（[OM 工作流与种子流程](../concepts/om-workflow-t1.md) 第 9 节，2026-08-04）。
2. ✅ 制造事务（资源/外协/间接费/报废/完工/任务关闭/期间关闭）分录（[成本管理事务会计分录](../concepts/cost-management-transactions-t1.md) 3.4，2026-08-04）。
3. ✅ e48842 Profile 默认值表（154 行 CSV：`sources/catalog/om_profile_defaults.csv`；页面见 [OM 关键 Profile 选项](../concepts/om-profile-options-t1.md) 附录 2，2026-08-04）。
4. 待获得权限后：eTRM 表字段、MOS 补丁差异、实例验证。

## 3. 失效链接清单（13 本，书单仍收录）

以下文档的 HTML 目录在官方书单中指向已失效的旧路径，未列入重点快照；如需使用建议先到 My Oracle Support 或新版文档库确认替代：

- Customer Data Librarian Implementation Guide（e48923）
- Customers Online Implementation Guide（e48933）
- Demantra 系列 6 本（e44444、e48801、e48802、e22233、e48807、e49182）
- Financials for Asia/Pacific User's Guide（e48762）
- Grants Accounting User Guide（e49015）
- In-Memory Consumption-Driven Planning User's Guide（e52281）
- Incentive Compensation Analytics for Oracle DI（e49152）
- Payables Reference Guide（e48763，PDF 可用）

> 2026-08-04 核验：13 本的 **PDF 在标准路径均可用（HTTP 200）**，已全部下载归档到 `sources/docs/<part>/<part>.pdf`；仅 HTML 目录链接失效。catalog 已补标准 PDF 链接（`scripts/fetch_ebs_catalog.py` 带兜底逻辑）。

## 4. 未下载内容

- 全集 393 本的 PDF/HTML 正文尚未批量下载（量大，且大部分域不在当前重点）。
- 建议后续按业务域分批：先 SCM/VCE/Financials 的 User/Implementation Guide 正文，再技术底座。
- 2026-08-04 已下载：13 本 legacy 文档 PDF（约 17MB）。

## 5. 权限缺口（无法仅靠公开文档补足）

| 信息类型 | 当前状态 | 需要的权限 |
| --- | --- | --- |
| 已知问题 / Bug / 补丁说明 | 不可得 | My Oracle Support 只读账号 |
| 完整表字段与 eTRM | 不可得（仅 f53031 用户指南） | EBS 实例 eTRM / 数据库字典只读 |
| 源码级调用链 | 不可得 | 合法安装实例 + Trace |
| 企业当前配置后的真实行为 | 不可得 | 企业实例只读访问 |
| 补丁差异 | 不完整 | MOS + 实例补丁清单 |

## 6. 下一步建议

1. 按“离散制造闭环”把 WIP/INV/成本文档正文逐章摄入（物料→BOM→工艺→任务→发放→移动→完工→成本→分录）。
2. 补销售订单到收款、采购到付款的闭环页面。
3. 争取 MOS 只读账号；争取 EBS 非生产环境只读访问（应用用户 + APPS 字典 + eTRM 责任）。
4. 每次官方文档更新后重跑 `scripts/fetch_ebs_catalog.py` 刷新目录，对比 Part Number 后缀变化。
