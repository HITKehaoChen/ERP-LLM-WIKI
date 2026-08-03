---
title: 内容索引
type: index
status: stable
updated: 2026-08-04
---

# 内容索引

> LLM 查询流程：先读本页，再钻取相关页面；需要原文时回 `sources/` 或官方链接。

## 总览与状态

- [知识库总览](overview.md) — 三层结构、信任等级、当前重点
- [覆盖率与缺口报告](coverage/report.md) — 文档全集/重点域覆盖、MOS 与实例缺口

## 业务域

- [Work in Process（WIP）](domains/work-in-process.md) — 任务、工序、物料、成本
- [Inventory（库存）](domains/inventory.md) — 物料主数据、组织、事务、批次/序列
- [Order Management（销售订单）](domains/order-management.md) — 订单录入到开票
- [Intercompany（关联交易）](domains/intercompany.md) — AGIS 与 GL/AR/AP/SLA 链路

## 业务流程

- [离散制造闭环（物料→BOM→WIP→完工→成本→分录）](processes/discrete-manufacturing-closed-loop.md)
- [销售订单履行到开票（规划中）](processes/sales-order-to-cash.md)
- [关联交易处理链路（规划中）](processes/intercompany-flow.md)

## 业务对象（entities）

- [WIP Job（离散任务）](entities/wip-job.md)
- [Sales Order（销售订单）](entities/sales-order.md)
- [Inventory Item（物料）](entities/inventory-item.md)
- [Intercompany Transaction（关联交易）](entities/intercompany-transaction.md)

## 概念（concepts）

- [Multiple Organizations 与 MOAC（规划中）](concepts/multiple-organizations.md)
- [成本方法：标准/平均/FIFO-LIFO（规划中）](concepts/costing-methods.md)
- [Subledger Accounting（SLA）事件模型（规划中）](concepts/subledger-accounting.md)
- [销售订单生命周期与状态机（T1）](concepts/order-lifecycle-and-status.md)
- [WIP 任务与重复性计划状态机（T1）](concepts/wip-job-status-machine.md)
- [Inventory 账户设置与科目推导（T1）](concepts/inventory-accounting.md)
- [SLA 成本事件模型（T1）](concepts/sla-costing-events.md)
- [AGIS 关联交易处理链路（T1）](concepts/intercompany-processing-t1.md)
- [OM 交易类型与默认规则（T1）](concepts/om-transaction-types-defaulting.md)
- [Shipping 发运状态与流程（T1）](concepts/shipping-statuses-and-processes.md)
- [WIP 物料控制与完工（T1）](concepts/wip-material-control-and-completions.md)
- [Intercompany Invoicing 与复杂关联交易（CIC）（T1）](concepts/intercompany-invoicing-t1.md)
- [Inventory 事务类型与处理模式（T1）](concepts/inventory-transaction-types.md)
- [SLA AMB 账户推导规则（T1）](concepts/sla-amb-account-derivation.md)
- [OM 工作流与种子流程（T1）](concepts/om-workflow-t1.md)
- [OM 关键 Profile 选项（T1）](concepts/om-profile-options-t1.md)
- [成本管理事务会计分录（T1）](concepts/cost-management-transactions-t1.md)
- [OM 数据模型概览（T1）](concepts/om-data-model-t1.md)
- [OM Open Interfaces 与 API（T2 社区转印）](concepts/om-open-interfaces.md)
- [Order-to-Cash 表级流程（T2 社区资料）](concepts/order-to-cash-with-tables.md)

## 来源页（sources）

- [来源页索引（63 份重点文档）](sources/index.md)
- raw 层目录说明：[sources/](../sources/README.md)

## 时间线

- [log.md](log.md) — 摄入/查询/健康检查记录
