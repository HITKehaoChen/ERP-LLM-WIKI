---
title: "Inventory（库存）"
type: domain
status: draft
verified: doc-only
sources: [e48820, e48822, e48823, e48824, e48828, e48830, e48825, e48826, e48799, e53453]
updated: 2026-08-03
---

# Inventory（库存）

## 一句话定位

Inventory 是物料主数据与库存事务的中枢：管理组织/子库/货位结构、物料定义与状态、批次/序列、单位换算、接收/发料/转移/盘点等全部库存事务，并向上游 WIP/OM、下游财务提供数据。

> 本文档当前为 **T2 文档归纳**，来源为官方章节结构；未逐章阅读正文，未做实例验证。

## 核心结构（[e48820 · “Inventory Structure”](../sources/e48820.md)）

- 组织与参数：[“Organization Parameters Window”](../sources/e48820.md)
- 子库：[“Defining Subinventories”](../sources/e48820.md)
- 货位：[“Defining Stock Locators”](../sources/e48820.md)
- 组织访问与组织间网络：[“Defining Organization Access”](../sources/e48820.md)、[“Inter-Organization Shipping Network”](../sources/e48820.md)
- 关联公司关系：[“Defining Intercompany Relations”](../sources/e48820.md) → 关联 [Intercompany 域](intercompany.md)

## 物料主数据（[e48820 · “Item Setup and Control”](../sources/e48820.md)）

- 主组织（Item Master Organization）与属性控制（[“Item Attribute Controls”](../sources/e48820.md)）
- 物料状态控制（[“Item Status Control”](../sources/e48820.md)）
- 模板、类别/类别集、交叉引用、物料目录
- 定义与维护（[“Defining and Maintaining Item Information”](../sources/e48820.md)）与 Open Item Interface 导入
- 属性组（Inventory/BOM/Costing/Purchasing/Work In Process/Order Management/Invoicing 等）→ 各模块共享同一物料主数据

## 批次/序列与状态

- 批次控制：[“Lot Control”](../sources/e48820.md)（批次属性、等级、批次谱系）
- 序列控制：[“Serial Number Control”](../sources/e48820.md)（生成、分配、谱系）
- 物料状态控制：[“Material Status Control”](../sources/e48820.md)

## 事务体系（[e48820 · “Transactions”](../sources/e48820.md)）

| 事务族 | 官方章节 |
| --- | --- |
| 接收 | [“Receiving Transactions”](../sources/e48820.md) |
| 退供应商 | [“Overview of Return to Vendor Transactions”](../sources/e48820.md) |
| 子库间转移 | [“Transferring Between Subinventories”](../sources/e48820.md) |
| 杂项事务 | [“Performing Miscellaneous Transactions”](../sources/e48820.md) |
| 组织间转移 | [“Inter-organization Transfers”](../sources/e48820.md) |
| 寄售/VMI | [“Transferring Consigned and VMI Material”](../sources/e48820.md) |
| 事务设置 | [“Transaction Setup”](../sources/e48820.md)（来源类型/动作/类型/原因/账户别名） |

事务管理器与待处理事务：[“Transaction Managers”](../sources/e48820.md)、[“Viewing Pending Transactions”](../sources/e48820.md)。

事务类型（来源类型+动作）、原因、账户别名与处理模式已 T1 化：
[Inventory 事务类型与处理模式（T1）](../concepts/inventory-transaction-types.md)。

## 与 WIP / OM / 财务的连接

- → WIP：组件发料/退料、完工入库（见 [WIP 域](work-in-process.md)）。
- → OM：ATP、预留、销售订单发货扣减（见 [Order Management 域](order-management.md)）。
- → 财务：库存事务经成本管理与 SLA 生成分录（[Cost Management](../sources/e48829.md)、[SLA 概念](../concepts/subledger-accounting.md)）。
- → 关联交易：组织间转移/关联公司关系是 Intercompany 前置设置（[Intercompany 域](intercompany.md)）。

## 相关文档

- [e48820 Inventory User's Guide](../sources/e48820.md)
- [e48828 / e48830 Warehouse Management](../sources/e48828.md) · [e48830](../sources/e48830.md)
- [e48825 / e48826 Mobile Supply Chain Applications](../sources/e48825.md) · [e48826](../sources/e48826.md)
- [e48799 Landed Cost Management](../sources/e48799.md)
- [e53453 Yard Management](../sources/e53453.md)
- [e48822 Consigned Inventory](../sources/e48822.md)
- [e48823 Copy Inventory Organization](../sources/e48823.md)
- [e48824 Movement Statistics](../sources/e48824.md)

## Open Questions / 留白

- 各事务类型的**账户/价值流推导规则**（读正文 + 实例验证）。
- 组织间转移与关联公司交易在 Inventory 侧的确切触发点。
- 企业实例的物料/组织/子库/账户配置（无权限，留白）。
- 表名与接口表（如 `MTL_TRANSACTIONS_INTERFACE`）需 eTRM/实例。
