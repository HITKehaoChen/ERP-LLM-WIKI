---
title: "WIP 物料控制与完工（T1）"
type: concept
status: stable
verified: doc-only
sources: [e48905]
updated: 2026-08-04
---

# WIP 物料控制与完工（T1）

> 本页为 **T1 官方文档原文**级知识，来源：Oracle Work in Process User's Guide（e48905）“Material Control”章。原始快照：[T228107T228115.htm](../../sources/docs/e48905/chapters/T228107T228115.htm)，官方 URL：https://docs.oracle.com/cd/E26401_01/doc.122/e48905/T228107T228115.htm

## 1. 发料与退料（Component Issues and Returns）

- 组件发料给任务/计划时，系统自动更新 Inventory 组件库存余额与 WIP 已发数量；完工时更新库存成品余额与任务完成数量；退回反向处理（[“Transactions and Balances”](../sources/e48905.md)）。
- 车间移动时，系统自动递减 From 工序/步骤余额、递增 To 工序/步骤余额。
- 特定组件可用 “Specific Component” 选项在 WIP Material Transactions 窗口手工发/退料。
- Phantom 组件：WIP 只识别 phantom 的组件清单（不识别 phantom 子装配本身）；组件成本并入上级成本；`BOM:Use Phantom Routings`（默认 No）决定 phantom 工艺资源成本是否计入上级；`BOM:Inherit Phantom Op Seq`（默认 Yes）决定组件是否继承上级工序号；ATO 模型/选项按 phantom 处理但成本不计入上级。

## 1.1 Supply Types（供应类型，T1）

来源：[e48905 · “Supply Types”](../sources/e48905.md)，原始快照 [T228107T228127.htm](../../sources/docs/e48905/chapters/T228107T228127.htm)。

| 类型 | 官方定义 |
| --- | --- |
| Assembly Pull | 完工入库时自动发料，从组件需求指定的供应子库拉取；无工艺路线的 BOM/任务必须用 Assembly Pull（而非 Operation Pull）；未指定装配的非标准任务不能使用。 |
| Operation Pull | 完成倒冲工序（backflush operation）时自动发料；不能用于无工艺路线装配、无工艺路线非标准任务、或工艺含禁用工序的装配。 |
| Push | 按需直接发料给任务/计划；可指定发料子库（默认组件供应子库）。 |
| Based on Bill | WIP 专用：任务/线装配关联默认该类型，组件按 BOM 中各自的供应类型供应；改为其他类型会应用到全部组件需求；无工艺路线但基于 BOM 的任务会把 Operation Pull 组件自动改为 Assembly Pull。 |
| Bulk | 可查看/上报表，但不需要事务处理；不倒冲、不默认全发；可手工对特定 Bulk 组件发料。 |
| Supplier | 供应商提供物料的提示性需求；不倒冲、不默认全发；可手工发料。 |
| Phantom | 只能赋给 BOM/Engineering 的组件子装配；WIP 中不能对任务/线装配分配；phantom 子装配失去独立身份，其组件直接并入上级（见上文 Phantom 规则）。 |

供应类型可在 Inventory 物料上或 BOM 组件上定义；WIP 定义任务时可改默认的 Based on Bill 类型，也可用 Material Requirements 窗口逐条改。

## 2. Backflush（倒冲）

### 触发点（官方列出）

- 用 Move Transactions 在工序上完成装配；
- 用 Move Transactions 移动并完成装配入库存；
- 用 Completion Transactions 完工入库；
- 在采购 Enter Receipts 窗口接收外协（OSP）装配；
- Open Move Transaction Interface / Inventory Transaction Interface 导入的移动/完工事务。

### 反向倒冲（Reverse Backflush）触发点

- 在工艺路线中移回上一步骤（Move Transactions）；
- 把已完工装配退回任务（Completion Transactions）；
- 采购 Enter Returns / Enter Corrections；
- 接口导入的退回/更正事务。

### Backflush 规则（官方原文）

- 组件必须定义启用的默认供应子库（及需要的货位）；
- 非标准任务必须指定工艺引用（Routing references）；
- 组件必须可事务（transactable）；
- `INV: Allow Expense to Asset Transfer` = No 时，倒冲子库必须是资产子库；
- 小数倒冲数量最多 5 位小数；
- `WIP: Ignore Zero Quantity Backflush` 控制小于 0.000005 的数量是否报错或处理（四舍五入为零时不生成库存事务）；
- 产量计算基于精确需求量；
- 修订控制的组件默认当前修订，可用 Component Revision Default During Backflush 客户端扩展改；
- 串行控制组件倒冲时，必须选含足够有效串号的子库/货位（不允许负库存例外）。

### 负库存

- `Allow Negative Balances` 参数控制是否允许负余额；`Override Negative for Backflush` Profile 可在倒冲时覆盖 No 设置（串行控制组件除外）。

### 供应子库

- 可在物料或 BOM 组件层定义供应子库/货位；未定义时用 WIP Backflush Supply Subinventory and Locator 参数。

## 3. 完工与退回（Assembly Completions and Returns）

### 完工事务类型

| 事务类型 | 官方定义 |
| --- | --- |
| WIP Assembly Completion | 从任务/计划收成品入库存；Assembly Pull 供应类型组件自动倒冲（批次/串号需识别；批号可按 WIP Backflush Lot Selection Method 参数手工或自动，串号必须手工）。有工艺路线时完工数量受最后工序 To move 步骤数量限制；无工艺路线时可超任务总量完工。 |
| WIP Assembly Return | 从库存退回成品到任务/计划；Assembly Pull 组件自动反向倒冲。可退回数量可超过已完工数（重复性计划/无工艺非标准任务；销售订单不能超过已完工数）。 |

### 完工/退回行为

- 有工艺路线：完工减少最后工序 To move 步骤数量、增加任务完成数量；退回反向。
- 完工子库默认来自任务或重复性线/装配关联；子装配可完工到上级供应子库；可改默认。
- 最终装配订单（FA）完工时预留自动按销售订单行交期从任务转移到子库/货位；退回 FA 必须输入销售订单行与交货信息。
- 批次/串号控制组件需选择倒冲批次/串号；WMS 环境支持 LPN 完工。
- 重复性线完工按 FIFO 分配到具体计划；退回按 LIFO。
- 修订控制：默认当前修订；串行装配可关联正确修订。
- 超完工：可在容差内超过任务起始数量完工（Assembly Over-completions）。
- 事务日期必须落在开放会计期间内，且不晚于当前日期、不早于任务发放日期（或最早有效重复性计划）。

## 4. 供应子库补货（Replenishment）

- 可整任务/计划补货，或按重复性生产天数补货；
- 方式 1：从任意子库/货位转到任务供应子库（可用于 Pull 组件暂存）；
- 方式 2：低层装配完工到下一层 BOM 的供应子库（feeder line 场景），完成即自动补货上层供应子库。

## 5. 库存准确性

- WIP 供应/完工子库可纳入循环盘点与物理盘点；Discrete Job Data Report / Repetitive Schedule Data Report 核对组件需求与已发数量；WIP Location Report 核对按工序的装配余额。

## 证据

- e48905 “Material Control”章：https://docs.oracle.com/cd/E26401_01/doc.122/e48905/T228107T228115.htm

## Open Questions

- Push 组件与 Operation Pull / Assembly Pull 的完整差异（e48905 “Supply Types” 章，待摄入）。
- 完工事务的账户推导（见 [SLA 成本事件模型（T1）](sla-costing-events.md) 与 [Inventory 账户设置与科目推导（T1）](inventory-accounting.md)）。
- 企业实例的 WIP 参数（Backflush 供应子库、负库存、Lot Selection）配置（无权限，留白）。
