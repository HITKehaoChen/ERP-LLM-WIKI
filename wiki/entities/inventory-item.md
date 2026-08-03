---
title: "Inventory Item（物料）"
type: entity
status: draft
verified: doc-only
sources: [e48820]
updated: 2026-08-03
---

# Inventory Item（物料）

## 定义

物料是 Inventory 的核心主数据对象，分**主组织级（Master Level）**与**组织级（Organization Level）**两层，属性按模块分组控制。见 [e48820 · “Overview of Items”](../sources/e48820.md)。

## 关键机制（T2 归纳）

- 主数据/组织级区别：[“Master Level vs. Organization Level”](../sources/e48820.md)
- 属性控制：[“Item Attribute Controls”](../sources/e48820.md)（属性组：Inventory/BOM/Costing/Purchasing/Work In Process/Order Management/Invoicing 等）
- 状态控制：[“Item Status Control”](../sources/e48820.md)（如草稿/有效/冻结）
- 类别与类别集：[“Item Category Flexfield Structures”](../sources/e48820.md)
- 模板：[“Item Templates”](../sources/e48820.md)
- 导入：[“Open Item Interface”](../sources/e48820.md)

## 生命周期

定义 → 状态控制生效 → 分配组织/子库 → 事务流转（收发/转移/盘点）→ 失效/删除（[“Item Deletion”](../sources/e48820.md)）。

> ⚠ 未验证：状态码与事务权限的具体规则需正文与实例核对。

## 相关页面

- [Inventory 域](../domains/inventory.md)
- [WIP 域](../domains/work-in-process.md)（物料被 BOM/任务引用）
- 来源：[e48820](../sources/e48820.md)
