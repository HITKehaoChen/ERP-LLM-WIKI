---
title: "销售订单到收款（规划中）"
type: process
status: draft
verified: doc-only
sources: [e48843, e48847, f10570]
updated: 2026-08-05
---

# 销售订单到收款（规划中）

> 本页为规划骨架，正文未读，仅列出已确认的官方章节入口。

表级流程（社区资料，含 OE/WSH/RA/AR/GL 表与状态码）见 [Order-to-Cash 表级流程（T2 社区资料）](../concepts/order-to-cash-with-tables.md)。

## 阶段

1. 订单录入 / 导入 → [e48843 · Order Capture / Order Import](../sources/e48843.md)
2. 预订 Book → [e48843 · Booking](../sources/e48843.md)
3. 履行（拣货/发运）→ [e48847 Shipping Execution](../sources/e48847.md)
4. 开票 → Receivables（[f10570 AR User Guide](../sources/f10570.md)）
5. 收款/核销 → Receivables / Payments

## 相关页面

- [Order Management 域](../domains/order-management.md)
- [Sales Order（实体）](../entities/sales-order.md)
