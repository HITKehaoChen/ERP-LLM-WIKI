---
title: "Inventory 账户设置与科目推导（T1）"
type: concept
status: stable
verified: doc-only
sources: [e48820, e48829]
updated: 2026-08-04
---

# Inventory 账户设置与科目推导（T1）

> 本页为 **T1 官方文档原文**级知识，来源：Oracle Inventory User's Guide（e48820）“Inventory Structure / Organization Parameters” 章。原始快照：[T291651T291796.htm](../../sources/docs/e48820/chapters/T291651T291796.htm)。

## 1. 估价账户（Valuation Accounts）

在组织参数（Organization Parameters）中定义默认估价账户；标准成本法下这些账户是子库默认值**可覆盖**；平均成本法下除 Expense 外的账户用于子库事务且**不可更改**。

| 账户 | 官方说明 |
| --- | --- |
| Material | 资产类，跟踪物料成本；平均成本法下存放库存与在途价值；发生事务后不可改。 |
| Material Overhead | 资产类，跟踪物料间接费成本。 |
| Resource | 资产类，跟踪资源成本。 |
| Overhead | 资产类，跟踪资源与外协间接费。 |
| Outside Processing | 资产类，跟踪外协成本。 |
| Expense | 非资产物料使用的费用账户。 |

## 2. 其他账户（Other Accounts）

| 账户 | 官方说明 |
| --- | --- |
| Sales | 损益类，默认收入账户。 |
| Cost of Goods Sold | 损益类，默认销货成本账户。 |
| Purchase Price Variance | 记录 PO 价与标准成本差异；平均成本法不用。 |
| Inventory A/P Accrual | 负债类，未匹配 AP 的采购收货（未开票收货）。 |
| Invoice Price Variance | PO 价与发票价差异；AP 匹配审批发票时使用。 |
| Encumbrance | PO 审批时确认资金预留的费用账户。 |
| Project Clearance | 资本项目杂项发料的分配账户。 |
| Average Cost Variance | 平均成本法负数量余额导致的估价误差。 |

**不同成本法的必设账户**（官方原文）：
- 标准成本法：Purchase Price Variance、Inventory A/P Accrual、Invoice Price Variance、Expense、Sales、COGS 必设。
- 平均成本法：Material、Average Cost Variance、Inventory A/P Accrual、Invoice Price Variance、Expense、Sales、COGS 必设。

## 3. 收货/差异账户参数（Other Accounts 页）

- **PPV 公式**：`PPV = (PO unit price − standard unit cost) × quantity received`，收货时入账；平均成本法不生成 PPV。
- **Invoice Price Variance**：`(PO 价 − 发票价) × 开票数量`，AP 匹配审批时入账，含汇率差异。
- **Inventory A/P Accrual**：采购收货时暂估应付款；发票匹配审批后由 AP 冲销。
- **Deferred COGS**：在 AR 确认收入前暂存成本。
- **Cost Variance / LCM Variance**：成本差异与落地成本差异账户。
- **On-Hand Adjustment / Lot Transaction Distribution**：按重量（catch weight）调整、批次增减等事务的默认账户。

## 4. 子库科目（Subinventory GL Account Fields）

| 子库科目 | 官方说明 |
| --- | --- |
| Material | 该子库物料成本累计，通常资产类；MRP/再订货点生成 PR 时作为默认，收货时用相应估价/费用账户。 |
| Outside Processing | 外协成本累计；WIP 收货时按标准成本记入，发料时按标准成本冲减。 |
| Material Overhead | 物料间接费（burden）累计，通常资产类。 |
| Overhead | 资源/部门间接费累计；WIP 完工入库时记入、发料时冲减。 |
| Resource | 资源成本累计；WIP 完工时记入、发料时冲减。 |
| Expense | 费用子库收货/资产子库收费用物料时记入。 |
| Encumbrance | 采购预留（Purchasing Only），用于 PO 收货与退货。 |

## 5. 组织间转移账户（Inter-Organization Transfer Accounts）

| 账户 | 官方说明 |
| --- | --- |
| Transfer Credit | 发货组织收取转移费用的默认账户（通常费用类）。 |
| Purchase Price Variance | 标准成本组织组织间收货 PPV 的默认账户（通常费用类）。 |
| Payable | 收货组织的组织间清算账户（通常负债类）。 |
| Receivable | 发货组织的组织间清算账户（通常资产类）。 |
| Intransit Inventory | 在途库存价值（通常资产类）；平均成本组织下默认物料账户。 |

## 6. 与 WIP / 成本的关系

- WIP 完工入库按标准成本记入子库 Material/Resource/Overhead/OSP 等账户，发料时冲减（见上表）。
- 这些账户最终经 Cost Management 的 SLA 事件模型生成完整分录（见 [SLA 事件模型](subledger-accounting.md) 与 [Cost Management](../sources/e48829.md)）。

## 证据

- e48820 “Valuation Accounts / Other Accounts / Inter-Organization Transfer Accounts / Subinventory General Ledger Account Fields”，官方 URL：https://docs.oracle.com/cd/E26401_01/doc.122/e48820/T291651T291796.htm

## Open Questions

- 具体事务类型（接收/发料/转移/盘亏）到科目的完整映射表（e48820 “Viewing Accounting Lines” 与 e48829 SLA 章节，待逐条整理）。
- 企业实例的组织参数与账户段值（无权限，留白）。
