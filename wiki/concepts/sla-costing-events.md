---
title: "SLA 成本事件模型（T1）"
type: concept
status: stable
verified: doc-only
sources: [e48829, e48771]
updated: 2026-08-04
---

# SLA 成本事件模型（T1）

> 本页为 **T1 官方文档原文**级知识，来源：Oracle Cost Management User's Guide（e48829）“SLA Costing Events - Accounting” 章。原始快照：[T372621T465151.htm](../../sources/docs/e48829/chapters/T372621T465151.htm)，官方 URL：https://docs.oracle.com/cd/E26401_01/doc.122/e48829/T372621T465151.htm

## 模型说明

成本管理通过 SLA 事件模型生成会计：每个**事件实体（Event Entity）**下有一组**事件类（Event Class）**，每个事件类映射若干**日记账行类型（Journal Line Type，JLT）**；具体选哪个 JLT 由**条件**决定（材料事件用 `ALT`，接收事件用 `RALT`，WIP 事件用 `ALT`）。完整条件代码见该章 “Event Class Journal Line Type Conditions” 与 “Legend”。

事件实体共 4 组：WIP Accounting Events、Receiving Accounting Events、Accrual Write-Off Events、Material Accounting Events。另附 Receiving/WIP/Inventory 的 Event Transaction Type Mapping。

## WIP Accounting Events

| Event Class | Journal Line Types | Event Type |
| --- | --- | --- |
| WIP Absorption | Work in Process Valuation、Resource Absorption、Estimated Scrap Absorption | Resource Absorption |
| WIP Absorption | Overhead Absorption、Resource Absorption | Overhead Absorption |
| WIP Absorption | Estimated Scrap Absorption | Resource Rate Variance |
| Outside Processing | Work in Process Valuation、Outside Processing、Resource Absorption、Overhead Absorption、Shop Floor Delivery for Direct Items、Receiving Inspection、IPV Transfer to Work Order、Purchase Price Variance、Offset | （外协相关事件） |
| WIP Variance | Work in Process Valuation、Period Close Variance、Work in Process Variance、Job Close Variance、Final Completion Variance | Period Close / Job Close / Final Completion |
| WIP Lot | Work in Process Valuation、Offset | WIP Lot Split / Merge / Update Quantity / Bonus |
| WIP Cost Update | Work in Process Valuation、Cost Update Adjustment | WIP Cost Update |

## Material Accounting Events

| Event Class | Journal Line Types | JLT Selected when |
| --- | --- | --- |
| PO Delivery into Inventory | Inventory Valuation (ALT=1)、Offset (ALT=2)、Material Overhead Absorption (ALT=3)、Receiving Inspection (ALT=5)、Purchase Price Variance (ALT=6)、Cost Variance (ALT=13)、Clearing (ALT=31)、Shikyu Variance (ALT=33) | 按 ALT 条件 |
| Sales Order Issue | Inventory Valuation (ALT=1)、Cost Variance (ALT=13)、Deferred COGS (ALT=36)、COGS (ALT=35)、Cost Update Adjustment (ALT=37) | 按 ALT 条件 |
| Internal Order to Expense | Inventory Valuation (ALT=1)、Offset (ALT=2)、Interorg Profit (OPM) (ALT=34) | 按 ALT 条件 |

## Receiving Accounting Events

| Event Class | Journal Line Types | JLT Selected when |
| --- | --- | --- |
| Receipt into Receiving Inspection | Accrual (RALT='Accrual')、Receiving Inspection、Clearing、Intercompany Accrual (IC Accrual)、Intercompany COGS (IC Cost of Sales) | 按 RALT 条件 |
| Delivery to Expense Destination | Charge、Receiving Inspection | 按 RALT |
| Period End Accrual | Accrual、Charge | 按 RALT |
| Retroactive Price Adjustment to Receipt | Accrual、Retroactive Price Adjustment、Intercompany Cost of Goods Sold、Receiving Inspection | 按 RALT |
| Retroactive Price Adjustment to Delivery | Retroactive Price Adjustment、Charge、Receiving Inspection | 按 RALT |

> 注：上表已按原文整理，但原文表格中“Event Class → JLT”逐行条件（ALT/RALT 代码）请以 raw 快照核对。

## 账户推导入口

- 事件类 + JLT 只是“记哪类账”的骨架；**科目本身**由 SLA 的 Account Derivation Rules（AMB：映射集、科目推导规则、Journal Line Types 定义）决定，见 [e48771 Subledger Accounting Implementation Guide](../sources/e48771.md) 的 “Accounting Methods Builder” 与 “Account Derivation Rules” 章节。
- 成本管理侧配置入口：[e48829 · “Defining Accounting Derivation Rules”](../sources/e48829.md)、Create Accounting / Transfer Journal Entries to GL 并发程序。

## ALT/RALT 条件表（Event Class Journal Line Type Conditions）

### WIP Accounting Events

| Event Class | Journal Line Types | Condition |
| --- | --- | --- |
| WIP Absorption | Work in Process Valuation / Estimated Scrap Absorption / Overhead Absorption / Resource Absorption / Resource Rate Variance | Accounting Line Type = 7 / 29 / 3 / 4 / 6 |
| Outside Processing | Work in Process Valuation / Resource Absorption / Overhead Absorption / Receiving Inspection / Purchase Price Variance / Offset | ALT = 7 / 4 / 3 / 5 / 6 / 2 |
| WIP Variance | Work in Process Valuation / Work in Process Variance | ALT = 7 / 8 |
| WIP Lot | Work in Process Valuation | ALT = 21 OR 22 OR 23 OR 24 OR 26 OR 28 |
| WIP Lot | Offset | ALT = 25 OR 27 |
| WIP Cost Update | Work in Process Valuation / Cost Update Adjustment | ALT = 7 / 2 |

### Receiving Accounting Events

| Event Class | Journal Line Types | Condition |
| --- | --- | --- |
| Receipt into Receiving Inspection | Accrual / Receiving Inspection / Clearing / Intercompany Accrual / Intercompany COGS | RALT = 'Accrual' / 'Receiving Inspection' / 'Clearing' / 'IC Accrual' / 'IC Cost of Sales' |
| Delivery to Expense Destination | Charge / Receiving Inspection | RALT = 'Charge' / 'Receiving Inspection' |

### Legend（官方缩写）

`AA`=Accounted Amount、`ALT`=Accounting Line Type、`LN`=Line Number、`RALT`=Receiving Accounting Line Type、`TAN`=Transaction Action Name。

### Event Transaction Type Mapping（摘要）

- 接收事件映射：Receive→Receipt into Receiving Inspection、Deliver→Delivery to Expense、Return to Supplier→Return to Vendor、Retroactive Price Adjustment to Receipt/Delivery、Logical Receipt、Period End Accrual 等（完整表见 raw 快照）。
- WIP 事件映射：Resource transaction→Resource Absorption、Overhead transaction→Overhead Absorption 等（完整表见 raw 快照）。

## Open Questions

- Material Accounting Events 的 ALT 条件（ALT=1/2/3/5/6/13/31/33/34/35/36/37）已在 [SLA 成本事件模型](sla-costing-events.md) 材料事件表列出，但各代码的业务含义（如 31=Clearing）需结合 e48829 其他章节核对。
- 事件交易类型映射（Receiving/WIP/Inventory）与具体事务的对应，待逐条核对。
- 企业实例的会计方法与科目规则（无权限，留白）。

## 相关页面

- [Inventory 账户设置与科目推导（T1）](inventory-accounting.md)
- [Subledger Accounting（SLA）事件模型（规划中）](subledger-accounting.md)
- [WIP 任务与重复性计划状态机（T1）](wip-job-status-machine.md)
