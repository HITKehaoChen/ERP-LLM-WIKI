---
title: "OM 工作流与种子流程（T1）"
type: concept
status: stable
verified: doc-only
sources: [e48844]
updated: 2026-08-04
---

# OM 工作流与种子流程（T1）

> 本页为 **T1 官方文档原文**级知识，来源：Oracle Order Management Using Oracle Workflow Guide（e48844）。原始快照：
> - 种子流程定义 [T393423T393429.htm](../../sources/docs/e48844/chapters/T393423T393429.htm)
> - 种子子流程定义 [T393423T393430.htm](../../sources/docs/e48844/chapters/T393423T393430.htm)
> - 处理/后台引擎/验证 [T393423T393427.htm](../../sources/docs/e48844/chapters/T393423T393427.htm) · [T393423T672274.htm](../../sources/docs/e48844/chapters/T393423T672274.htm)

## 1. 种子工作流文件与 Item Type

- 种子数据文件：`oexwford.wft`（OM 主工作流）、`ctochord.wft`（CTO 变更单）。
- Item Types：`OM Change Order`、`OM Order Header`、`OM Order Line`。
- 工作流通过交易类型（Transaction Types）窗口分配给订单/行流程；行流程随行类型分配。

## 2. 头级种子流程（OM Order Header Processes）

- Order Flow - Generic（通用订单流）
- Order Flow - Generic with Booking Approval（带预订审批）
- Order Flow - Return with Approval（退货审批流）
- Order Flow - Mixed or Return with Approval（混合/退货审批流）
- CTO Change Order Process：配置项已创建后修改计划发运日/请求日/行数量/配置，或取消订单时自动触发；按 ATO/CTO/PTO 类型向规划员或采购员发通知（直运行不发此通知）。
- Change Order Process：其他订单变更的“变更通知”流程（Actions > Notification 手工触发）。
- ISO 系列（内部销售订单变更管理）：ISO Cancel、ISO Line Cancel、ISO Qty update、ISO Schedule Date update、ISO Quantity and Schedule Date update、ISO Item Update —— 变更后通知内部申请（Internal Requisition）编制人。

## 3. 头级子流程（OM Order Header Subprocesses）

- Approve Return - Order（返回 Complete / Incomplete；未授权时更新状态 Reject – Pending Cancellation）
- Approve Return – Order with Mixed Lines（未授权时订单状态 Return Rejected、待取消行 Rejected – Pending Cancellation）
- Book - Order, Deferred / Manual / Manual with AME Approval
- Close - Order
- Header Level Invoice Interface - Order

## 4. 行级子流程（OM Order Line Subprocesses，种子清单）

Authorized to Ship - Line、Buy ATO Item Flow、Calculate Lead Time - Line、Close - Line、Create ATO Supply、Create Configuration - Line, Manual、Create Manufacturing Configuration Data - Line, Manual、Create Supply - Line、Create Supply Order - Line, Manual、Create Work Order - Line、Enter - Line、Export Compliance Screening - Line、Header Level Invoice Interface - Line, Deferred、Header Level Invoice Interface for Return Line w/o Receipt / with Receipt、Internal Approval – Negotiation with AME、Approve Return – Order with Mixed Lines AME、Inventory Interface Non-Ship - Line（及 Deferred）、Invoice Interface - Line（及 Deferred）、Purchase Release - Line, Deferred（及 - ATO、Manual）、Reprice - Line、Return Receiving - Line、Schedule - Line（及 Deferred）、Ship - Line, Manual、Wait to Firm - Line、Wait to Fulfill Line。

## 5. 协商与销售协议子流程

- Negotiation：Submit Draft、Complete、Internal Approval、Customer Acceptance、Offer Expiration。
- Sales Agreement：Execute - Blanket、Terminate - Blanket、Close - Blanket、Blanket Agreement/Sales Order Generation、Notifications。

## 6. 处理机制

- **Workflow Background Engine**：预订等耗时活动可后台处理（配合 [销售订单生命周期与状态机（T1）](order-lifecycle-and-status.md) 的 BOOK_PROCESS_DEFER）；有性能指南（批量大小/轮询间隔）。
- **HVOP**：高量订单处理专用流程。
- **验证**：Transaction Types 窗口校验工作流分配；另有 “Validate OM Workflow” 并发程序校验种子/自定义流程。
- 错误处理：Workflow 错误进 WFERROR（RETRY_ONLY）错误流程，通知管理员重试；预期错误/重定价错误/异常管理见 Troubleshooting 章。

## 7. 关键子流程活动（官方函数与结果）

| 子流程 | 活动（函数） | 行为要点 |
| --- | --- | --- |
| Enter - Line | Wait for Booking（WF_STANDARD.WAITFORFLOW）→ End | 等待订单头预订后才继续行流。 |
| Book - Order, Manual | Start(DEFER) → Book - Eligible（STANDARD_BLOCK）→ Book（OE_BOOK_WF.BOOK_ORDER，结果含 Handles Holds）→ Book - Continue Line | 手工确认可预订后执行预订；预订完成才结束。 |
| Close - Order | Wait → Close - Wait for Line（WAITFORFLOW）→ Close → End(Complete)/End(Not Eligible) | 等全部行关闭后关闭订单头；On Hold/Incomplete 继续等待，Not Eligible 结束。 |
| Schedule - Line | Schedule（OE_OEOL_SCH.SCHEDULE_LINE）→ Schedule - Eligible（BLOCK）→ End | Incomplete/On Hold 时等待手工 Progress；Not Eligible/Complete 结束。 |
| Ship - Line, Manual | Ship（OE_SHIPPING_WF.START_SHIPPING）→ End | 结果：Ship Confirm / Non Shippable / Unreserved / Over Shipped Beyond Tolerance（超容差发通知）。 |
| Invoice Interface - Line | Invoice Interface（OE_INVOICE_WF.INVOICE_INTERFACE）→ End / Wait for Required for Revenue or Delivery | Complete/Not Eligible 结束；On Hold/Incomplete 等待手工 Progress；Partial 等 RFR/Delivery；Full Billing from Service Contracts 时 Not Eligible（Billed from Contracts）；Pre Billing Acceptance 先查验收。 |

各活动明细（Activity→Function→Result Type→Required）见 e48844 种子子流程章正文与 raw 快照。

## 8. 主流程活动（官方原文）

| 流程 | 活动/子流程 | 说明 |
| --- | --- | --- |
| Order Flow - Generic | Enter（WF_STANDARD.NOOP）→ End | 头级最小流程。 |
| Order Flow - Generic with Booking Approval | Enter → Book - Order, Manual with AME Approval → Close - Order | 预订前走 AME 审批：状态 Pending Internal Approval；拒绝→Review Required；批准→Booked；无审批人时同步预订，有审批人时异步。 |
| Order Flow - Generic with Header Level Invoice Interface | Enter → Book - Order, Manual → Header Level Invoice Interface - Order → Close - Order | 全部行履行完成后按订单头级接口开票，订单关闭才结束；须与 Line Flow - Generic with Header Level Invoice Interface 配套。 |
| Order Flow - Return with Approval / Mixed or Return with Approval | Approve Return（或 AME 变体）子流程 | 授权返回 Complete，未授权 Incomplete 并更新状态（Reject – Pending Cancellation / Return Rejected）。 |
| Line Flow - Generic | Fulfill - Deferred（DEFER）→ Fulfill（OE_FULFILL_WF.START_FULFILLMENT）→ End | 行级最小流程；Fulfill 后进入子流程（Schedule→Ship→Invoice Interface→Close）。 |
| Line Flow - Generic, Performance | Wait for Booking → Schedule（OE_OEOL_SCH.SCHEDULE_LINE）→ Branch on Source Type（ATO Item/Build/Dropship/Ship）→（Create Configuration / Create Supply Order / Purchase Release - Deferred）→ Fulfill → Invoice Interface（Partial→Wait RFR/Delivery）→ Close - Continue Header | 与 Generic 功能相同但子流程内联，性能优化；错误处理用 OMERROR/R_ERROR_RETRY。 |

行级各变体（ATO Item/ATO Model/Configuration/RLM/Export Compliance/Bill Only/Ship Only/Repricing/Return 系列/Standard Service）的活动表均在本章正文。

## 9. 各工作流变体活动（T1，官方活动表）

来源：e48844 “Seeded Workflow Definitions” 章（[T393423T393429.htm](../../sources/docs/e48844/chapters/T393423T393429.htm)）。

### 头级流程

| 流程 | 活动（函数） |
| --- | --- |
| Order Flow - Generic | Enter（NOOP）→ End（NOOP） |
| Order Flow - Generic with Header Level Invoice | Enter（NOOP）→ End（NOOP）（Book/Invoice/Close 为子流程） |
| Order Flow - Return with Approval | Enter（NOOP）→ End（NOOP）（Approve Return 为子流程） |

### 行级主流程

| 流程 | 活动（函数） |
| --- | --- |
| Line Flow - ATO Item | Fulfill - Deferred（DEFER）→ Fulfill（OE_FULFILL_WF.START_FULFILLMENT）→ End |
| Line Flow - ATO Model | Fulfill - Deferred → Fulfill → End（子流程：Enter/Schedule/Create Configuration/Invoice Interface Deferred/Close） |
| Line Flow - Configuration | Start（NOOP）→ Fulfill - Deferred → Fulfill → End |
| Line Flow - Configuration with Authorize to Ship (RLM) | Start → Configuration - Check Status（CTO_WORKFLOW.CHECK_RESERVATION_STATUS_WF，结果 Config Data Results）→ Fulfill - Deferred → Fulfill → End |
| Line Flow - Generic | Fulfill - Deferred → Fulfill → End |
| Line Flow - Generic with Authorize to Ship (RLM) | Fulfill - Deferred → Fulfill → End |
| Line Flow - Generic with Export Compliance | Fulfill - Deferred → Fulfill → End |
| Line Flow - Generic, Bill Only / Bill Only with Inventory Interface | Fulfill → End |
| Line Flow - Generic, Ship Only / with Repricing at Fulfillment | Fulfill - Deferred → Fulfill → End |
| Line Flow - Standard Service | Fulfill - Deferred → Fulfill → End |

### 退货/信贷行流程

| 流程 | 活动（函数） |
| --- | --- |
| Return for Credit Only | End（其余为子流程） |
| Return for Credit Only with Approval | Wait for Approval（WAITFORFLOW）→ End |
| Return for Credit Only with Approval and Hdr Inv | Enter – Line → Wait for Approval → Fulfill - Deferred → Fulfill → Header Level Invoice Interface for Return Line w/o Receipt → Close - Line → End |
| Return for Credit with Receipt | Fulfill - Deferred → Fulfill → End |
| Return for Credit with Receipt and Approval | Wait for Approval → Fulfill - Deferred → Fulfill → End |
| Return with Receipt Only, No Credit | Fulfill - Deferred → Fulfill → End |

> 说明：部分表格在主流程层只列 Fulfill/End，其余动作（Schedule/Ship/Invoice/Close）由子流程承载；个别表解析仅得 End 行的以原文为准。

## 证据

- e48844：https://docs.oracle.com/cd/E26401_01/doc.122/e48844/T393423T393429.htm（流程）、T393423T393430.htm（子流程）

## Open Questions

- 每个种子流程的活动明细表（Start→Activity→End 节点与函数），在 e48844 正文中，待逐流程整理。
- 企业实例的交易类型→工作流映射（无权限，留白）。
