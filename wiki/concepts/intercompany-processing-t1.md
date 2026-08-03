---
title: "AGIS 关联交易处理链路（T1）"
type: concept
status: stable
verified: doc-only
sources: [e48781]
updated: 2026-08-04
---

# AGIS 关联交易处理链路（T1）

> 本页为 **T1 官方文档原文**级知识，来源：Oracle Advanced Global Intercompany System User's Guide（e48781）第 “Intercompany Transaction Processing” 章与 “Intercompany Open Interface Tables” 附录。原始快照：[T463896T463900.htm](../../sources/docs/e48781/chapters/T463896T463900.htm)、[T463896T463903.htm](../../sources/docs/e48781/chapters/T463896T463903.htm)。

## 1. 交易方向与页面

- **Outbound（发起方）**：在 Outbound Batches 页按批次创建交易，可包含任意多个接收方；两步：先录批次头与交易，再录批次费用/收入分摊（distributions）。
- **Inbound（接收方）**：在 Inbound Transactions 页查看/更新/批准/拒绝收到的交易。
- 分摊（Distribution）模式：Automatic 模式下提交时按接收方交易数**按交易数分摊**（不是按接收方数）；Manual 模式由发起方手工录入 Initiator/Recipient 会计。
- 交易账户默认由 SLA 的 **Transaction Account Builder** 生成；未设置规则时可手工录入。发起方 AR 账户与接收方 AP 账户在交易**批准后**自动生成。
- 更新仅可在 `Received` 状态进行；批准/拒绝需要用户被设为接收方组织的联系人；若系统选项 “Allow Recipient to Reject Transactions?” = No，则不能拒绝。

## 2. 批号编号

- 批号是批次唯一控制号；系统选项可选 **System Generated**（建批时自动生成）或 **Manual**（手工维护编号）。
- 系统生成编号基于数据库序列（database sequence），保证唯一；手工编号按“数据库实例 + 发起方组合”校验唯一。

## 3. 工作流通知

- 发起方/接收方工作流做校验并按间隔通知状态；校验失败时发通知给相应用户。
- 用户必须被设置为发起方或接收方组织的联系人才能收到通知。

## 4. 转总账（Transfer to GL）

**不需要发票的交易批准后直接转 GL。** 转前必须满足：

- 设置页的 transfer options 已配置；
- GL 对应期间开放；
- 交易状态为 Approved；
- 若币种不同，存在汇率；
- 已指定交易日期用于汇率计算。

模式：

- **Online**：批准时发起方/接收方工作流自动转移，无需干预；
- **Batch**：运行或调度 “Transfer Intercompany Transactions To General Ledger” 并发程序（参数：GL Date 区间、Ledger/LE/Intercompany Org 区间、Run Journal Import、Create Summary Journals 等）。

后续步骤（两种模式都要）：

1. AGIS 只把交易写入 **GL Interface 表**；
2. 运行或调度 **GL Journal Import** 并发程序导入日记账；
3. GL 的 **Posting** 过程把日记账过账到实际账户。

成功后状态变化：发起方/接收方工作流分别置为 `Transferred to Initiator GL` / `Transferred to Recipient GL`；双方都转完后批次与交易状态置为 `Complete`。

## 5. 转应收/应付（Transfer to AR/AP）

- 发起方工作流把交易转到 **Receivables** 创建发票；AR 创建发票后回写发票号给接收方工作流，接收方再更新并转 **Payables**。
- 前置条件：System Options 设置好 transfer options；Invoicing Options 中映射 Receivables Transaction Type / Memo Line；定义 Customer-Supplier 关联（Customer Supplier Associations / Trading Partners）。

## 6. 撤回与冲销

- 只有已提交给接收方审批的批次/交易可 **Recall**（撤回）。
- 只有 Approved 或 Complete 的批次/交易可 **Reverse**（冲销）；冲销方式：Switch Debit/Credit 或 Change Sign。

## 7. Open Interface 表（导入接口）

导入程序状态：`Accepted` / `Rejected`。核心接口表与关键字段（官方附录）：

| 表 | 关键字段/规则 |
| --- | --- |
| FUN_INTERFACE_CONTROLS | Group_id（序列 fun_interface_controls_s）、Source；Source + Group_ID 构成唯一键；Request_id / Date_Processed 由导入程序更新。 |
| FUN_INTERFACE_BATCHES | Batch_id、Batch_Number（同一发起方唯一）、Initiator_id/Name、From_Le_id/Name、From_Ledger_Id（可推导）、Control_Total（占位，非交易合计）、Running_Total_Cr/Dr（**一个批次必须全为贷或全为借**）、Currency_Code（**批内交易同一币种**）、Trx_Type_Id/Name/Code（**批内交易同一类型**，三者至少填一个）、Gl_Date、Reject_Allow_Flag、Import_Status_Code。 |
| FUN_INTERFACE_HEADERS | Trx_id、Trx_Number、Recipient_id/Name、To_Le_id/To_Ledger_Id（可推导）、Batch_id、Invoicing_Rule_Flag（Y=需开票转 AR；N=转 GL）、Initiator/Recipient_Instance_Flag、Description、Import_Status_Code。 |
| FUN_INTERFACE_DIST_LINES | Trx_id、Dist_id、Party_id、Party_Type_Flag（I=发起方 / R=接收方）、Dist_Type_Flag（必须为 L）、Import_Status_Code。 |

## 8. 状态与术语

- 交易状态：Received → Approved（→ Rejected 或 Recall/Reverse 分支）→ Transferred to Initiator/Recipient GL（或 AR/AP 流程）→ Complete。
- 前置设置（[e48781 · “Intercompany Setup”](../sources/e48781.md)）：Intercompany Accounts、Balancing Rules、Organizations、Transaction Types、Periods、Invoicing Options、Customer-Supplier Associations、System Options、SLA 默认账户规则。

## Open Questions

- AGIS 文档为 E48781-06（2019）；最新补丁对页面/程序的改动需 MOS 确认。
- 复杂关联交易（CIC：Inventory Intercompany Invoicing）在 [e48820 “Intercompany Invoicing”](../sources/e48820.md) 与 [e48829 “Complex Intercompany Invoicing”](../sources/e48829.md)，待整理为另一页。
- 企业实例的 AGIS 系统选项、账户规则与批号序列（无权限，留白）。

## 相关页面

- [Intercompany 域](../domains/intercompany.md)
- [Intercompany Transaction（实体）](../entities/intercompany-transaction.md)
- [SLA 成本事件模型（T1）](sla-costing-events.md)
