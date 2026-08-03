---
title: "成本管理事务会计分录（T1）"
type: concept
status: stable
verified: doc-only
sources: [e48829]
updated: 2026-08-04
---

# 成本管理事务会计分录（T1）

> 本页为 **T1 官方文档原文**级知识，来源：Oracle Cost Management User's Guide（e48829）：
> - 标准成本事务 [T372621T373688.htm](../../sources/docs/e48829/chapters/T372621T373688.htm)
> - 平均成本库存事务 [T372621T374058.htm](../../sources/docs/e48829/chapters/T372621T374058.htm)
>
> 重要前提（官方原文）：以下为**默认账户**；启用 SLA 且自定义规则后不再使用默认账户。

## 1. 标准成本法 · 分销组织事务

### 采购收货到库存（一步）

第一步（按 PO 价）：

| 账户 | 借 | 贷 |
| --- | --- | --- |
| Receiving Inspection @ PO Cost | XX | — |
| Inventory A/P Accrual @ PO Cost | — | XX |

第二步（按标准成本）：

| 账户 | 借 | 贷 |
| --- | --- | --- |
| Subinventory 账户 @ 标准成本 | XX | — |
| Receiving Inspection @ PO Cost | — | XX |
| （差额）Purchase Price Variance | 借/贷 | 借/贷 |

有物料间接费时：Subinventory 借（含间接费），Material Overhead Absorption 贷（独立一条）。

### 退供应商

- 从接收检验退：Inventory A/P Accrual 借、Receiving Inspection 贷（冲回原收货分录）。
- 从库存退（无接收检验）：与直接收货到库存相同的账户、反向金额（Accrual 借、Receiving Inspection 贷）。
- 外币按 PO 价换算为账套币种。

### 销售订单发运

| 账户 | 借 | 贷 |
| --- | --- | --- |
| Deferred COGS | XX | — |
| Subinventory 账户 @ 标准成本 | — | XX |

费用子库/费用物料发运**不产生会计**。

### RMA 收货

| 账户 | 借 | 贷 |
| --- | --- | --- |
| Subinventory 账户 @ 标准成本 | XX | — |
| COGS（及 Deferred COGS 拆分） | — | XX |

## 2. 标准成本法 · 制造事务（WIP 已安装）

### 组件发料/退料

- 发料：WIP accounting class valuation 账户借（标准成本）、Subinventory elemental 账户贷。
- 退料：反向。

### 移动/倒冲事务

- 移动事务可触发操作完成倒冲、自动按标准费率计资源与间接费；向后移动自动反向 Operation Pull 倒冲。
- 倒冲发料分录与组件发料相同（WIP valuation 借、Subinventory elemental 贷）。

### 其他制造事务

- Resource Charges、Outside Processing Charges、Overhead Charges、Assembly Scrap、Assembly Completion、Job Close、Period Close、WIP Cost Update 均在 e48829 本章逐项给出分录（正文待逐条摘录）。

## 3. 平均成本法 · 库存事务

> 平均成本法账户来自**交易关联的成本组（Cost Group）**，不是组织级账户；组织级是默认，可在成本组级覆盖（创建事务前）。

### 杂项事务

- 发料到 GL 账户/别名：Entered G/L account 借、Organization Valuation accounts 贷（均按当前平均成本）；收货反向。可输入事务单位成本替代当前平均成本（注意对剩余库存平均成本的影响）。
- 费用子库/费用物料：发到账户时按无价值移动数量（假设已消耗）；资产子库转移按当前成本；费用物料收货到资产/费用子库均无会计。

### 子库间转移

- 借/贷同一个 Valuation 账户（平均成本组织只有一套估价账户）；WMS/项目组织可多成本组多套账户。

### 循环盘点/物理盘点

- 盘多（实际 > 账面）：Organization Valuation 借、Adjustment 账户贷（按当前平均成本）；盘少反向。
- 费用子库/费用物料无分录，但修正数量余额。
- 建议：冻结物理盘点后、调整前不要做影响平均成本的事务。

## 3.1 FIFO/LIFO（层成本法）事务

来源：[T372621T375126.htm](../../sources/docs/e48829/chapters/T372621T375126.htm)

- 杂项发料：Entered G/L account 借、Inventory Valuation accounts 贷（按层成本）；收货反向；可输入事务单位成本替代层成本。
- 子库间转移：使用同一套组织估价账户，整体库存价值净影响为零。
- 盘点/物理盘点：盘多 → Valuation 借、Adjustment 贷；盘少反向（均按层成本）；费用子库/费用物料无分录。
- PO 收货到接收检验：Receiving Inspection @ PO cost 借、Inventory A/P Accrual @ PO cost 贷（PO 行无价格时按零估值）。
- 接收检验→库存交付：Organization Material @ PO cost 借、Receiving Inspection @ PO cost 贷，**在 PO 价建立新层**；有物料间接费时 Subinventory 借、Material Overhead Absorption 贷。
- 费用项/费用子库收货：Subinventory Expense @ PO cost 借、A/P Accrual 贷。
- 外币：PO 成本换算成账套币种后入账并重算层成本。

## 3.2 项目制造成本（Project Manufacturing Costing）

来源：[T372621T378169.htm](../../sources/docs/e48829/chapters/T372621T378169.htm)

- 项目成本组（Project Cost Groups）：不同项目/普通库存可有不同成本，普通库存归组织默认成本组；在途发运用**发出成本组**成本。
- Project Cost Collector：事务跨项目边界（项目↔非项目、项目间）或跨任务时，把成本转到 Oracle Projects 接口表；同项目同任务内不转移。
- 事务分录（默认账户，SLA 自定义后不适用）示例：PO 收货到接收检验（Receiving Inspection @ PO Cost / A/P Accrual，不转 Projects）、交付到库存（Cost Group Material @ PO Cost / Receiving Inspection，转 Projects）、PO 直接收货到库存（两步分录，转 Projects）、销售订单发运（后续表格在原文）。

## 3.3 周期成本（Periodic Costing）

来源：[T372621T378952.htm](../../sources/docs/e48829/chapters/T372621T378952.htm)

- 处理顺序：Periodic Acquisition Cost Processor →（可选）Acquisition Cost Adjustment Processor → Periodic Cost Processor →（可选）Distributions Processor → 其他活动 → 报表 → 关账 → 转 GL。
- 取得成本 = 采购取得相关成本之和（材料、运费、特别费用、不可回收税）；LCM 启用时用 LCM 计算的落地成本。
- 发票匹配收货：用发票价；无发票用 PO 价；汇率按发票时点 / Match to PO / Match to Receipt 决定。
- 部分期间运行必须从期间首日开始；全部成本组处理完整才能关账；期间开放时可重跑取得成本处理器（会清除旧结果），关闭后用 Periodic Cost Update 手工调整。

## 4. 相关页面

- [Inventory 账户设置与科目推导（T1）](inventory-accounting.md)
- [WIP 物料控制与完工（T1）](wip-material-control-and-completions.md)
- [SLA 成本事件模型（T1）](sla-costing-events.md)

## Open Questions

- 资源/外协/间接费/报废/完工/关闭/期间关闭/成本更新事务的分录逐条摘录（e48829 本章正文，待整理）。
- 层成本/项目成本/周期成本的**制造事务**（完工、差异）分录逐条摘录。
