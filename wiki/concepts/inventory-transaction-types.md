---
title: "Inventory 事务类型与处理模式（T1）"
type: concept
status: stable
verified: doc-only
sources: [e48820]
updated: 2026-08-04
---

# Inventory 事务类型与处理模式（T1）

> 本页为 **T1 官方文档原文**级知识，来源：Oracle Inventory User's Guide（e48820）“Transaction Setup”章。原始快照：[T291651T291655.htm](../../sources/docs/e48820/chapters/T291651T291655.htm)。

## 1. 事务类型 = 来源类型 + 动作

**事务类型（Transaction Type）是事务来源类型（Source Type）与事务动作（Action）的组合**，用于报表/查询分类，也用于 ABC 分析与预测的历史用量计算。

### 种子事务类型（部分，官方表）

| 名称 | 说明 | Source Type | Action |
| --- | --- | --- | --- |
| Reverse Staging Transfer | 为欠发物料自动创建 Move Order 申请 | Move Order | Subinventory Transfer |
| Return to Vendor | 从库房退供应商 | Purchase order | Issue from stores |
| Return to Organization | 按内部申请发运退回源组织或其他组织 | Internal Requisition | Issue from stores |
| Transfer to Regular | 转入常规库存 | Purchase Order | Ownership Transfer |
| Sales order issue | 外部销售订单 Ship Confirm | Sales order | Issue from stores |
| WIP Completion Return | 从库房退回装配给 WIP | Job or schedule | Assembly return |
| WIP Issue | 从库房发料到 WIP | Job or schedule | Issue from stores |
| Standard cost update | 更新标准成本信息 | Standard cost update | Cost update |
| RMA Receipt | 退货授权收货 | RMA | Receipt into stores |
| Internal RMA Receipt / Intransit / Canceled Intransit | 内部 RMA 各形态收货 | Internal RMA | Receipt/Intransit receipt |
| Return To Organization Intransit Shipment | 把在途发运退回源组织 | Internal requisition | Intransit shipment |
| Catch Weight Positive/Negative Adjustment | 按重量调整 | Inventory | Issue/Receipt into stores |
| Canceled Intransit Shipment Receipt | 取消 IOT 发运的 ASN 收货 | Inventory | Intransit receipt |
| Project Transfer | 项目制造中转移到项目 | Inventory | Subinventory transfer |
| Return to Vendor without Receipt | 未收货直接退供应商 | Inventory | Issue from stores |

另有 Staging Transfer、Ownership Transfer、Logical Issue/Receipt/Intercompany Sales、Retroactive Price Adjustment、Lot Split/Merge/Translate/Update、Container Pack/Unpack/Split、Cost Group Transfer、Delivery Adjustment 等。

### 用户自定义事务类型

- 只能选**预定义动作** + **自定义来源类型**的组合（例如来源 Charity + 动作 Issue from Stores → “Issue to Charity”）。
- 可选动作示例（官方）：Assembly completion、Assembly return、Cost update、Direct organization transfer、Intransit shipment、Issue from stores、Negative component issue、Negative component return、Receipt into stores、Staging transfer。
- 杂项收发、子库间转移、WIP 事务、组织间转移都必须指定事务类型。

## 2. 事务原因（Transaction Reasons）

- 原因用于分类/解释事务，可挂工作流；Reason Type 示例：Cycle Count、Drop、Load、QA Update Status、Receiving、Shipping、Shipping Backorder、Update Status（Replenishment 类型被禁用）。
- Load 类型有 Reason Context：Curtail Pick、LPN Exception、Pick None、Pick Over、Pick Partial、Change Source Locator、Change UOM。
- 原因可设失效日期。

## 3. 账户别名（Account Aliases）

- 账户别名是 GL 科目号的易记名称，事务中可用别名代替科目号；别名来自 Account Alias Name 键弹性域的段。
- 已引用过的别名不能再改科目；有效日期必须 ≥ 当前日期；失效日期 ≥ 生效日期与当前日期。

## 4. 事务处理模式（TP:INV Transaction Processing Mode）

- On-line：前台同步处理；可用 Server Side On-line Processing Profile 选择服务端处理（默认），通过 Inventory Remote Procedure Manager 执行。
- Background：后台处理，事务经表单校验后即可看到“可事务数量”，但未完成处理前不进事务报表/查询。
- Form level：按事务类型各自配置处理方式。
- 并发/后台模式适合大批量事务；也可通过 Open Transaction Interface 接入条码等设备。

## 5. 事务管理器（Transaction Managers）

- 管理器运行：material transaction、demand reservation、move transaction、resource cost transaction、remote procedure call、material cost transaction。
- **必须启动 material cost transaction manager 才能成本化物料事务**；外协收货后要移动到下一工序需 move transaction manager。
- 全部在线处理且不用事务接口时可不启动管理器；多 worker 支持并行批处理。

## 证据

- e48820 “Transaction Setup”章：https://docs.oracle.com/cd/E26401_01/doc.122/e48820/T291651T291655.htm

## Open Questions

- 全部种子事务类型清单（官方指引到 Transaction Types 窗口查询；eTRM/实例可查全量）。
- 每种事务类型对应的**科目推导**（结合 [Inventory 账户设置与科目推导（T1）](inventory-accounting.md) 与 [SLA 成本事件模型（T1）](sla-costing-events.md) 使用）。
- 企业实例的事务类型/来源类型/原因/别名配置（无权限，留白）。
