---
title: "Order Management（销售订单）"
type: domain
status: draft
verified: doc-only
sources: [e48843, e48842, e48844, e48847, e48846, e48845, e48832, e48848, e48849]
updated: 2026-08-04
---

# Order Management（销售订单）

## 一句话定位

Order Management 是销售订单从录入、预订（Book）、工作流履行、发运到开票的**订单履行中枢**，向下游接入 Shipping/INV、向上游对接定价/信用/AR。

> 本文档当前为 **T2 文档归纳**，来源为官方章节结构；未逐章阅读正文，未做实例验证。

## 订单模型（[e48843 · “Sales Orders Workbench”](../sources/e48843.md)）

- 订单头/行：[“Defining Sales Order Main and Other Header Information”](../sources/e48843.md)、[“Defining Sales Order Line Item Main Information”](../sources/e48843.md)
- 交易类型：[“Overview of Transaction Types”](../sources/e48843.md)
- 状态：完整状态机已升级为 T1 级，见 [销售订单生命周期与状态机](../concepts/order-lifecycle-and-status.md)
- 版本与审计：[“Versioning Overview”](../sources/e48843.md)、[“Order Audit Trail”](../sources/e48843.md)

## 主流程（按官方章节归纳）

1. **录入**：Sales Orders Workbench / Quick Sales Orders / Order Import（[“Order Import”](../sources/e48843.md)）或高量处理 HVOP。
2. **预订**：[“Booking”](../sources/e48843.md)（手动 `BOOK_PROCESS_ASYNCH` / 延迟 `BOOK_PROCESS_DEFER`）。
3. **履行**：[“Fulfillment in Oracle Order Management”](../sources/e48843.md)，由 Workflow 驱动（[e48844 OM Using Workflow](../sources/e48844.md)）。
4. **发运**：Shipping Execution（[e48847](../sources/e48847.md)），Ship Set / Arrival Set / 发运计划（[“Shipment Schedules”](../sources/e48843.md)）。
5. **开票**：接口到 Receivables（[“Invoicing and Payments”](../sources/e48843.md)）。

## 关键机制

- 定价：[“Pricing”](../sources/e48843.md) + [e48846 Advanced Pricing Implementation](../sources/e48846.md) / [e48845 User's Guide](../sources/e48845.md)
- ATP/预留/排程：[“ATP, Reservations, and Scheduling”](../sources/e48843.md)
- 配置：ATO/PTO、Configure to Order（[e48832](../sources/e48832.md)）
- 订单变更/批量变更/重定价：[“Order Changes”](../sources/e48843.md)、[“Applying Mass Changes”](../sources/e48843.md)
- 退货：RMA / Credit Orders（[“Defining Return Material Authorizations”](../sources/e48843.md)）
- 销售协议：Sales Agreements（[“Sales Agreements”](../sources/e48843.md)）
- 直运：Drop Shipments（[“Drop Shipments Overview”](../sources/e48843.md)）
- 发布管理：Release Management（[e48848](../sources/e48848.md) / [e48849](../sources/e48849.md)）

交易类型与默认规则已 T1 化：[OM 交易类型与默认规则（T1）](../concepts/om-transaction-types-defaulting.md)；
发运状态与 Ship Confirm 规则已 T1 化：[Shipping 发运状态与流程（T1）](../concepts/shipping-statuses-and-processes.md)。
种子工作流与子流程清单已 T1 化：[OM 工作流与种子流程（T1）](../concepts/om-workflow-t1.md)。

## 与 WIP / INV / 财务的连接

- → WIP：Back-to-Back 订单、FA 订单自动创建（[WIP 域](work-in-process.md) 的 “Linking Sales Orders and Discrete Jobs”）。
- → Inventory：ATP、预留、发货扣减、WMS（[Inventory 域](inventory.md)）。
- → AR：开票与收款（[Intercompany / 财务域](intercompany.md)）。

## 相关文档

- [e48843 Order Management User's Guide](../sources/e48843.md)
- [e48842 Order Management Implementation Manual](../sources/e48842.md)
- [e48844 OM Using Oracle Workflow](../sources/e48844.md)
- [e48847 Shipping Execution User's Guide](../sources/e48847.md)
- [e48846 / e48845 Advanced Pricing](../sources/e48846.md) · [e48845](../sources/e48845.md)
- [e48832 Configure to Order Process Guide](../sources/e48832.md)
- [e48848 / e48849 Release Management](../sources/e48848.md) · [e48849](../sources/e48849.md)

## Open Questions / 留白

- 状态**转换矩阵**的完整整理（状态清单与关键规则已 T1，逐条转换仍在整理）。
- 实施手册（e48842）中的交易类型/默认规则/处理约束正文。
- 企业实例的交易类型、默认规则、定价上下文（无权限，留白）。
- 表名/字段（如 `OE_ORDER_HEADERS_ALL`）与 Order Import 接口表需 eTRM/实例。
