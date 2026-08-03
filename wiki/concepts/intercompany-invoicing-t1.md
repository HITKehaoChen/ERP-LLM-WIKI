---
title: "Intercompany Invoicing 与复杂关联交易（CIC）（T1）"
type: concept
status: stable
verified: doc-only
sources: [e48820, e48829]
updated: 2026-08-04
---

# Intercompany Invoicing 与复杂关联交易（CIC）（T1）

> 本页为 **T1 官方文档原文**级知识，来源：
> - Oracle Inventory User's Guide（e48820）“Intercompany Invoicing”章：[T291651T292529.htm](../../sources/docs/e48820/chapters/T291651T292529.htm)
> - Oracle Cost Management User's Guide（e48829）“Complex Intercompany Invoicing”章：[T372621T379162.htm](../../sources/docs/e48829/chapters/T372621T379162.htm)

## 1. 总体业务流程（官方原文）

1. 客户向**销售经营单位（selling OU）**下单；
2. 订单从与销售 OU **不同的发货 OU** 的仓库发货给客户；
3. 发货 OU 按**转移价（transfer price）**向销售 OU 开**关联应收发票（intercompany AR）**；
4. 销售 OU 向发货 OU 开**关联应付（intercompany AP）**；
5. 若客户为外部客户，销售 OU 另向客户开正常发票。

## 2. 前置设置

- 定义销售/发货 OU 之间的 **Intercompany Relations**；
- 定义 **Intercompany Transaction Flows**（交易流）；
- 定义价格表（Price Lists）；
- 定义 AR / AP 系统选项；
- 在 AR/AP 定义一致的税务结构（税码与税率）；
- 设置 COGS 账户的 **Account Generator**；
- 定义内部与外部客户、供应商与供应商地点（用于 AP 发票）、给每个库存组织分配经营单位；
- 物料在 Master 与 Organization 级启用，并启用 Customer Ordered / Customer Order Enabled / Internal Ordered 等属性。

## 3. 相关 Profile Options

| Profile | 说明 |
| --- | --- |
| INV:Intercompany Currency Conversion | 外币发票的汇率类型。 |
| INV:Inter-company Invoice for Internal Orders | 允许为内部订单（在途发运、内部 RMA 收货/在途/取消在途收货）创建关联发票；Site 级设置。 |
| INV:Use Transfer Price From Intercompany AR With Internal Order RMA | 默认 Yes：贷项金额按父级在途发运关联 AR 发票的转移价计算；No 时按价格表转移价功能计算。 |
| INV:Advanced Pricing for Inter-company Invoice | 启用 Advanced Pricing 计算关联发票；需安装 AP。 |
| Tax:Allow Override of Tax Code / Tax:Invoice Freight as Revenue / Tax:Inventory Item for Freight | 运费税码、运费是否作为收入行、作为收入行时使用的物料。 |
| MO:Operating Unit | 每个职责设置正确的经营单位。 |

> Create Intercompany AR Invoices 程序按职责读取 Profile：同一 OU 内各职责值不一致时报错；未设置时用 Site 值。

## 4. 交易流（Transaction Flows）

- 交易流定义**财务路径**（哪些 OU/库存组织参与成本、负债转移与收入确认），可与实物流动不同；逻辑交易（Logical transaction）是 OU 之间的会计事件，不伴随实物移动。
- 类型：**Shipping flow**（发货 OU ≠ 销售 OU）与 **Procuring flow**（收货 OU ≠ 采购 OU）。
- 可选 Ship From/To Organization、类别限定（shipping 用库存类别集，procuring 用采购类别集）；
- Procuring flow 需选 Asset price / Expense price：`PO` 或 `Transfer`；
- Advanced Accounting 勾选（多 OU 自动勾选）后 Organization 与 To OU 必填，可用 Nodes 定义中间 OU 链；
- 修改流程用 End Date 关闭旧流程再建新流程。

## 5. 会计分布（Accounting Distributions）

- 所有关联发票使用预定义批源（batch source）**intercompany**，修改可能导致 AutoInvoice 意外失败；使用销售代表科目段时需将 Allow Sales Credit Flag 设为 Yes。
- 币种：按**销售 OU 的币种/开票地点**记账（示例：销售 OU 在英国、发货 OU 在美国 → 按英镑开票并换算成美元）；运费/手续费/关税/保险与转移价不同币种时需另开一张关联发票。
- 币种选择规则（官方表，摘要）：
  - Shipping + 未用 Advanced Pricing → Price List 币种；
  - Shipping + Advanced Pricing → 按所选（Shipping OU / Selling OU / Order 币种）决定；
  - Procuring + PO Price → 采购（From）OU 币种；Transfer Price → 价格表币种或 From/To OU 币种（取决于 Advanced Pricing 与选择）。
- 科目来源（AutoAccounting + Open Interface 导入 AR）：
  - Salesperson 科目段：来自 no sales credit default 的账户；
  - 标准行科目段：来自物料主数据 Sales Account；
  - 运费行科目段：Freight 作为物料时来自物料（配合 Tax profile），否则来自标准备忘行 `intercompany freight`；
  - Invoice Type 科目段：来自 Intercompany Relations 中定义的发票类型。
- 检查 AR 发票前必须：事务处理器完成订单发料、事务已成本化、AutoInvoice 对 source=Intercompany 无错误完成；AP 发票检查前需 AR 发票已创建、Create Intercompany AP Invoices 已成功、Invoice Import（source=intercompany）已完成。

## 6. 复杂关联交易（CIC）会计示例（e48829）

场景：OU1 接客户订单（$25）→ OU2 发货（仓库）→ OU2 不备料，OU3 全球采购（PO $10）→ 供应商直发 OU2 → OU2 物理收货，OU3 做 PO 收货并向 OU2 发运（转移价 $15）→ OU1 做向客户发运，OU2→OU1 做转移交易（转移价 $20）→ OU1 收货。

OU3 会计分录（官方示例）：

| 处理器 | 借方 | 贷方 |
| --- | --- | --- |
| Receiving Processor | OU1 Clearing 10 | Accrual 10 |
| Cost Processor | OU2 Inventory 10 | OU1 Clearing 10 |
| Invoicing | Intercompany Receivable 15 | Intercompany Revenue 15 |
| Cost Processor | Intercompany COGS 10 | OU2 Inventory 10 |

OU2 会计分录（官方示例）：

| 事务 | 处理器 | 借方 | 贷方 |
| --- | --- | --- | --- |
| Receipt | Receiving Processor | OU1 Clearing 15 | Intercompany Accrual 15 |
| Receipt | Intercompany Invoicing | Intercompany Accrual 15 | Intercompany Payable 15 |
| Deliver | Cost Processor | OU1 Inventory 15 | OU1 Receipt 15 |
| Shipping | Intercompany Invoicing | Intercompany Receivable 20 | OU1 Intercompany Revenue 20 |
| Shipping | Cost Processor | Intercompany COGS 15 | OU1 Inventory 15 |

OU1 会计分录（官方示例）：

| 事务 | 处理器 | 借方 | 贷方 |
| --- | --- | --- | --- |
| Shipping | Cost Processor | OU3 Inventory 20 | OU1 Inventory 20 |
| Shipping | Intercompany Invoicing | Intercompany Accrual 20 | Intercompany Payable 20 |
| Shipping | Cost Processor | OU3 COGS 20 | OU3 Inventory 20 |
| AR Invoicing | Accounts Receivable Invoicing | OU3 Receivable 25 | OU3 Revenue 25 |

> “drop ship across ledgers”“ownership transfer”“shared procurement”等场景与 OU 链完整分录均在本章正文（[T372621T379162.htm](../../sources/docs/e48829/chapters/T372621T379162.htm)）。

## 7. 与 AGIS 的关系

- AGIS 处理“纯财务”关联交易（[AGIS 关联交易处理链路（T1）](intercompany-processing-t1.md)）；
- CIC/Intercompany Invoicing 处理**伴随实物/内部订单流**的关联开票与所有权转移；两者会计都进 GL，规则分别在 e48781 与 e48820/e48829。

## Open Questions

- 企业实例的 Intercompany Relations、交易流、价格表与科目规则（无权限，留白）。
