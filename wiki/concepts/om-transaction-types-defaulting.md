---
title: "OM 交易类型与默认规则（T1）"
type: concept
status: stable
verified: doc-only
sources: [e48842]
updated: 2026-08-04
---

# OM 交易类型与默认规则（T1）

> 本页为 **T1 官方文档原文**级知识，来源：Oracle Order Management Implementation Manual（e48842）“Order Entry Tools：Transaction Types” 与“Defaulting”章节。原始快照：[T373258T377073.htm](../../sources/docs/e48842/chapters/T373258T377073.htm)（交易类型）、[T373258T377247.htm](../../sources/docs/e48842/chapters/T373258T377247.htm)（变更管理/处理约束）。

## 1. 交易类型基础（Transaction Types）

- 交易类型是销售单据（订单/退货/报价/销售协议）的**通用术语**，与 Receivables Transaction Type 是完全不同的对象。
- 交易类型代码（Transaction Type Code）取值 `Order` 或 `Line`，决定它是订单类型还是行类型。
- **先定义行类型**，行类型要分别为订单行与退货行定义；名称必须唯一（不能存在同名订单类型与行类型）。
- 行类型要点：
  - Order Category 取 `Order` 或 `Return`；
  - 字段可用性受限：Order Workflow、Default Return/Order Line Type、Agreement Required、Purchase Order Required、信用检查规则等对行类型不可用；
  - Agreement Type 用于行校验；Price List 可作默认源，Enforce List Price 决定订单录入时能否手工打折；
  - Shipping 页的 Inspection Required 决定退货行收货时是否要求检验；
  - 调度级别 5 选 1：ATP Only、Allow all scheduling actions、No reservations、Inactive Demand with Reservations、Inactive Demand without Reservations。
- 订单类型要点：
  - Order Category 取 `Mixed` / `Order` / `Return`（决定订单内允许的行类型）；
  - 指定履行流（Fulfillment flow），报价可再指定协商流（Negotiation flow）；报价/销售协议只有头流程，无行流程；
  - Retain Document Number：从协商阶段进入履行阶段时是否保留原单据号；
  - Agreement Required / Purchase Order Required 勾选后，Booking 时强制要求；
  - Credit Check 规则决定该类型是否做信用检查（留空=不检查）；
  - Minimum Margin Percent：低于最低毛利时 Booking 时挂 Margin Hold（需启用 Calculate Margin）；
  - Autoschedule 决定是否自动排程。

## 2. 单据编号（Document Sequence）

- 订单号由订单交易类型绑定的**文档序列**控制（编号方法：Automatic / Manual / Gapless）；创建序列与绑定是两步，不能在交易类型窗口直接完成。
- 创建订单类型时系统自动创建同名 Document Category，并创建两个序列类别：同名（订单用）与“同名-quote”（报价用）。
- 销售协议（Sales Agreements）**只使用自动编号**。

## 3. 开票相关默认（Finance Tab）

- Invoicing Rule / Accounting Rule 作默认源传给 AutoInvoice。
- Invoice Source、Non-Delivery Invoice Source、Receivables Transaction Type 不在订单头/行上保存，发票接口活动执行时按以下顺序取值：**行交易类型 → 订单交易类型 → Profile Option**；找不到则发票接口失败。
- 贷项通知单（Credit Memo）交易类型默认顺序：行类型 → 订单类型 → Profile（多经营单位时忽略 Profile 值）。
- Cost of Goods Sold Account 供库存接口在 Ship Confirm 时使用。

## 4. Enforce List Price 标志

- 勾选后订单录入时不允许手工打折（Freight Charges 仍会计算，因为它们不改变售价）。
- 对 Pricing 和 Availability 及 Order Import 窗口不生效。
- Pricing 不支持该标志：Price 事件时 Calculate Price Flag=Y，后续事件（Save/Book）置为 P（Partial），只计算 Freight。

## 5. 默认规则框架（Defaulting）

- 默认对象分实体（Entity：Order Header / Order Line）与属性（Attribute）；描述性弹性域不由默认框架控制。
- **条件（Conditions）**：控制何时查哪组默认源；每种实体种子条件 `ALWAYS` 必须放在默认条件优先级**最后**；同 Group Number 的规则按 AND 连接，不同组按 OR。
- **来源（Sources）**：Constant Value、Application Profile、Same Record、Related Record、System Variable（可用表达式如 `sysdate + 7`）、PL/SQL API、其他。
- **顺序**：Defaulting Sequence 决定属性默认先后，同号按字母序；条件有 Precedence，来源有 Sequence。
- **依赖（Dependencies）**：属性变更会级联更新依赖属性；仅勾选 “Include in Building Defaulting Conditions” 的属性可用于条件。

## 6. 处理约束（Processing Constraints）

- 处理约束按**操作（Operation）**定义，如 `CANCEL`；用 Require Reason / Require History 与模板（如 Entered / Booked）设定“取消点”。
- 用户约束不能比系统约束更宽松；系统约束禁止：已关闭/已取消订单行、已发运/已开票行、已接收或已贷记的退货行、已收货的直运行。
- 详见 [销售订单生命周期与状态机（T1）](order-lifecycle-and-status.md) 第 7 节。

## 证据

- e48842 “Transaction Types” 章：https://docs.oracle.com/cd/E26401_01/doc.122/e48842/T373258T377073.htm
- e48842 “Change Management / Processing Constraints” 章：https://docs.oracle.com/cd/E26401_01/doc.122/e48842/T373258T377247.htm

## Open Questions

- 种子交易类型清单与各字段默认值（在正文表格中，待整理）。
- Profile Option 全表（e48842 设置章 T373258T374215.htm，待摄入）。
- 企业实例的交易类型→工作流映射（无权限，留白）。
