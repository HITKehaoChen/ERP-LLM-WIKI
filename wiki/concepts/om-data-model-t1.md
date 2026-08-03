---
title: "OM 数据模型概览（T1）"
type: concept
status: stable
verified: doc-only
sources: [e48842]
updated: 2026-08-05
---

# OM 数据模型概览（T1）

> 本页为 **T1 官方文档原文**级知识，来源：Oracle Order Management Implementation Manual（e48842）附录 “Data Model Overview”。原始快照（R12.2）：[T373258T376736.htm](../../sources/docs/e48842/chapters/T373258T376736.htm)。
> 用户提供的 R12.1 等价链接：https://docs.oracle.com/cd/E18727_01/doc.121/e13406/T373258T376736.htm

## 1. 业务对象与实体

销售订单是一个业务对象，包含：

- **Header Level**：Order Header、Header Sales Credits、Sales Agreement Order Header。
- **Line Level**：Order Lines、Sales Agreement Order Lines、Line Sales Credits、Line Price Adjustments、Line Pricing Attributes、Line Adjustment Attributes、Line Adjustment Associations、Lot Serial Numbers。

要点（官方原文）：
- 很多原本在头级的属性现在也在行级（如 Bill To 行级化，同一订单不同行可开票到不同地点）；头级属性用于默认行级。
- Order Cycle 已被 **OM Workflow Definitions** 取代；Order Type 已被 **OM Transaction Types** 取代。
- 新 Order Line 合并了旧 SO_HEADERS / SO_ORDER_LINES / SO_LINE_DETAILS 的属性。
- 行级独立：每行有自己独立的流程（按行类型的工作流分配），可不同于头流程。

## 2. 行（Shipment）模型

- **每行即一个 Shipment**；行五元组（Line Number, Shipment Number, Option Number, Component Number, Service Number）在界面上显示为 1.1.1.1.1。
- `OE_ORDER_LINES_ALL` 存储 Shipments、Options、Included Items、Configuration Item Lines；LINE_SET_ID 把同一原始行拆出的 shipment 连起来；TOP_MODEL_LINE_ID 指向配置顶层 Model（Model 行指向自身）；LINK_TO_LINE_ID 指向直接父行；ITEM_TYPE_CODE 标识 STANDARD/MODEL/CLASS/OPTION/INCLUDED ITEM；ATO_LINE_ID 指向 ATO Model 行。
- Ordered Quantity 表示**开放数量**（非原始数量）；取消被建模为“开放数量减少 + 取消数量增加”；提供原因的数量变更把旧记录存到 `OE_ORDER_LINES_HISTORY`。
- 部分处理触发**行拆分**：Ship-Confirmation、Return Receipt、Drop-ship Receipt；配置部分处理可产生成比例/非成比例拆分（后者产生 remnant set）。
- 行级状态：Core statuses 反规范化到行上（Open/Closed、Booked、Fulfilled）；`FLOW_STATUS` 列存行流摘要状态；`OE_LINE_STATUS_PUB` API 提供功能状态（含行流完成情况）。

## 3. 关键模块（官方原文）

### Cancellations

- 可直接改行开放数量做部分取消；标准行取消的系统种子约束被放到 ship-confirmation 或 invoice interface（no-ship 流）之后，可自定义更严约束。
- 取消**不走工作流**；行上 canceled quantity 表示是否发生过取消，Order/Line 的 canceled flag 表示是否完全取消；完全取消时头/行流强制到 close 活动。
- 规则决定“数量减少何时视为取消”；超过阈值才要求取消原因。

### Defaulting Framework

- PL/SQL 默认规则 + 条件；更新记录**不会级联**到已有子记录（如改头级仓库不影响已有行），可用 Mass Change 批量更新。
- 依赖 AK 字典；来源：same record、related record、profile、自定义 API 等。

### Fulfillment

- 由 fulfillment events 与 sets 驱动；种子事件：Ship-Confirmation、Purchase Release Receipt、Return Receipt；配置隐式视为 fulfillment set。
- 行可属于一个或多个 fulfillment set；全部成员履行后才通过 Fulfillment 活动。
- 行上有 fulfilled flag / fulfilled quantity；Over/Under Shipment 容差影响是否视为 fulfilled。

### Mass Change

- 按记录集批量更新属性，也可复制、重定价、排程、挂 Hold。

### Processing Constraints Framework

- PL/SQL 条件（来源含 Workflow Activity Statuses、自定义 API）；可按职责做包含/排除规则；OM 对订单对象的每次 insert/update/delete 都检查约束。
- 种子约束比 R11 更少更宽松（如“预订后不能删行”为兼容升级而种子化，可删除）；约束阻止时可通知有权限的人。

### Sets

- Ship Set / Arrival Set：拆 Ship Set 时系统提示（允许）；部分发运的 Ship Set 行自动退出 Set；任一成员 Ship Confirm 后 Set 自动关闭。
- 拆分行创建 Line Set（OE_SETS），公共属性（Item、数量 UOM、发运容差）存在 Line Set 上；Ship/Arrival 集合成员反规范化在 Order Line；fulfillment set 成员存 `OE_LINE_SETS`。

### System Parameters

- OU 级控件：Item Validation Organization、Customer Relationships Enabled Flag；账套从 AR 设置读取，无需 OM Profile 冗余设置。

### Transaction Types

- 同时存 Order Type 与 Line Type；头级专属控件（如订单编号）、行级专属控件（如行是否内部/外部来源）；Order 交易类型 category（ORDER/RETURN/MIXED）控制是否混排出入库行。
- 头工作流按 Order Type 分配；行工作流按 Order Type + Line Type + Item Type 组合分配；同一订单可含不同行类型、走不同流程。

## 4. 证据

- e48842 附录 “Data Model Overview”（R12.2）：https://docs.oracle.com/cd/E26401_01/doc.122/e48842/T373258T376736.htm
- R12.1 等价章节（用户提供）：https://docs.oracle.com/cd/E18727_01/doc.121/e13406/T373258T376736.htm

## Open Questions

- 各实体的完整表/字段（eTRM 为准，本文档只给概念与关键列）。
- 企业实例的表数据分布（无权限，留白）。
