---
title: "Sales Order（销售订单）"
type: entity
status: stable
verified: doc-only
sources: [e48843]
updated: 2026-08-04
---

# Sales Order（销售订单）

## 定义

销售订单是 Order Management 的核心对象，采用**订单头 + 订单行**结构：头承载客户、交易类型、日期、币种等，行承载物料、数量、价格、发运与开票信息。见 [e48843 · “Sales Orders Workbench”](../sources/e48843.md)。

## 订单头/行

- 头信息：[“Defining Sales Order Main and Other Header Information”](../sources/e48843.md)
- 行信息：[“Defining Sales Order Line Item Main Information”](../sources/e48843.md)、[“Defining Sales Order Line Shipping Information”](../sources/e48843.md)
- 交易类型决定默认流程：[“Overview of Transaction Types”](../sources/e48843.md)

## 生命周期（T1，详见状态机页）

| 阶段 | 说明 | 官方章节 |
| --- | --- | --- |
| 录入 | 手工/订单导入/高量处理 | [“Order Capture”](../sources/e48843.md)、[“Order Import”](../sources/e48843.md) |
| 预订 | 状态从 Entered 到 Booked | [“Booking”](../sources/e48843.md) |
| 履行 | Workflow 驱动（拣货/发运/开票） | [“Fulfillment in Oracle Order Management”](../sources/e48843.md) |
| 关闭 | 行完成/关闭/取消 | [“Close Orders”](../sources/e48843.md) |

完整状态清单、Booking/Fulfillment/Invoice/Cancel/Close 规则见
[销售订单生命周期与状态机（T1）](../concepts/order-lifecycle-and-status.md)。

## 相关页面

- [Order Management 域](../domains/order-management.md)
- [销售订单到收款（规划）](../processes/sales-order-to-cash.md)
- [WIP Job](wip-job.md)（销售订单可驱动任务创建）
- 来源：[e48843](../sources/e48843.md)
