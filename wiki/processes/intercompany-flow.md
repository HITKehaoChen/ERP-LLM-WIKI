---
title: "关联交易处理链路（规划中）"
type: process
status: draft
verified: doc-only
sources: [e48781, e48747, e48771]
updated: 2026-08-03
---

# 关联交易处理链路（规划中）

> 本页为规划骨架，正文未读，仅列出已确认的官方章节入口。

## 阶段

1. 前置设置：AGIS 设置 + Inventory Intercompany Relations + 多组织 → [e48781 · Intercompany Setup](../sources/e48781.md)、[e48833 Multi-Org](../sources/e48833.md)
2. 录入/导入 → [e48781 · Intercompany Transaction Processing](../sources/e48781.md)
3. 批号/审批 → [e48781 · Batch Numbering / Workflow Notifications](../sources/e48781.md)
4. 转 GL / 转 AR-AP → [e48781 · Transfers](../sources/e48781.md)
5. SLA 分录与 GL 过账 → [e48771 Subledger Accounting](../sources/e48771.md)、[e48747 GL](../sources/e48747.md)

## 相关页面

- [Intercompany 域](../domains/intercompany.md)
- [Intercompany Transaction（实体）](../entities/intercompany-transaction.md)
