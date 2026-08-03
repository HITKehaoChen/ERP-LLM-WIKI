---
title: "Intercompany Transaction（关联交易）"
type: entity
status: stable
verified: doc-only
sources: [e48781]
updated: 2026-08-04
---

# Intercompany Transaction（关联交易）

## 定义

关联交易是 AGIS 处理的核心对象：一条交易描述集团内两个经营单位之间的往来（金额/币种/账户/日期等），经批号组织、工作流审批后，转入总账或在 AR/AP 间互开单据。见 [e48781 · “Intercompany Transaction Processing”](../sources/e48781.md)。

## 处理链路（T2 归纳）

1. 录入/导入：[“Intercompany Transaction Page”](../sources/e48781.md)、[“Importing Intercompany Transactions”](../sources/e48781.md)（Open Interface Tables）。
2. 批号：[“Intercompany Batch Numbering Sequence”](../sources/e48781.md)。
3. 审批通知：[“Workflow Notifications”](../sources/e48781.md)。
4. 转出：[“Transferring Transactions to General Ledger”](../sources/e48781.md)、[“Transferring Transactions to Receivables and Payables”](../sources/e48781.md)。

完整 T1 规则（状态、批次编号、转 GL/AR-AP、接口表）见
[AGIS 关联交易处理链路（T1）](../concepts/intercompany-processing-t1.md)。

## 关键属性（T2 归纳）

- 交易双方（From/To Legal Entity 或 Operating Unit）
- 金额、币种、日期
- 批号与状态
- 账户/科目信息（转入 GL 用）

> ⚠ 未验证：接口表字段与状态机需读正文 + eTRM/实例。

## 相关页面

- [Intercompany 域](../domains/intercompany.md)
- [关联交易处理链路（规划）](../processes/intercompany-flow.md)
- 来源：[e48781](../sources/e48781.md)
