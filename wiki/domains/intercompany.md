---
title: "Intercompany（关联交易）"
type: domain
status: draft
verified: doc-only
sources: [e48781, e48783, e48836, e48747, e48748, e48749, e48761, e48760, e48763, f10310, f10570, f10312, e48771, e48750, e48751, e48768, e48766]
updated: 2026-08-04
---

# Intercompany（关联交易）

## 一句话定位

关联交易指**同一企业集团内不同法人/经营单位之间**的交易。Oracle EBS 的核心工具是 **AGIS（Advanced Global Intercompany System）**：集中录入/导入交易、生成批号、通知审批，并把结果转入总账或自动在 AR/AP 之间互开单据。

> 本文档当前为 **T2 文档归纳**；AGIS 指南版本较旧（E48781-06，2019），复杂关联交易（CIC）细节分布在 Cost Management 等文档中，需进一步核对。

## 主流程（[e48781 AGIS User's Guide](../sources/e48781.md)）

1. **设置**：[“Setting up AGIS”](../sources/e48781.md)（公司间关系、账户规则等前置设置）。
2. **录入/导入**：Intercompany Transaction Page（[“Intercompany Transaction Processing”](../sources/e48781.md)）或 [“Importing Intercompany Transactions”](../sources/e48781.md)（Open Interface Tables）。
3. **批号与通知**：[“Intercompany Batch Numbering Sequence”](../sources/e48781.md)、[“Workflow Notifications”](../sources/e48781.md)。
4. **转出**：
   - 转总账：[“Transferring Transactions to General Ledger”](../sources/e48781.md)
   - 转应收/应付：[“Transferring Transactions to Receivables and Payables”](../sources/e48781.md)
5. **报告**：[“Intercompany Reporting”](../sources/e48781.md)。

处理链路（批次/审批/转 GL/AR-AP、接口表）已整理为 T1 页：
[AGIS 关联交易处理链路（T1）](../concepts/intercompany-processing-t1.md)。

## 关联交易的多种形态（T2 归纳）

| 形态 | 涉及的模块/文档 |
| --- | --- |
| AGIS 集中处理 | [e48781](../sources/e48781.md) |
| 组织间转移 + 关联公司开票 | [e48820 · Intercompany Relations](../sources/e48820.md)、[e48829 · Complex Intercompany Invoicing](../sources/e48829.md) |
| 集团内部销售/采购订单 | Order Management + Purchasing 链路（待深入） |
| 会计分录 | GL（[e48747](../sources/e48747.md)）+ SLA（[e48771](../sources/e48771.md)） |

## 与财务模块的连接

- **GL**：交易转入总账并生成对方分录（[e48747 GL Implementation](../sources/e48747.md)、[e48748 GL User's Guide](../sources/e48748.md)）。
- **AR/AP**：AGIS 自动生成应收/应付单据（[f10310 AR Implementation](../sources/f10310.md)、[e48761 AP Implementation](../sources/e48761.md)）。
- **SLA**：关联交易的分录规则由 SLA 事件模型驱动（[e48771 Subledger Accounting](../sources/e48771.md)、[SLA 概念](../concepts/subledger-accounting.md)）。
- **E-Business Tax**：跨法人交易涉税（[e48750 / e48751 E-Business Tax](../sources/e48750.md) · [e48751](../sources/e48751.md)）。

## 相关文档

- [e48781 Advanced Global Intercompany System User's Guide](../sources/e48781.md)
- [e48783 Financials Implementation Guide](../sources/e48783.md)、[e48836 Financials Concepts](../sources/e48836.md)
- [e48747 / e48748 / e48749 General Ledger](../sources/e48747.md) · [e48748](../sources/e48748.md) · [e48749](../sources/e48749.md)
- [e48761 / e48760 / e48763 Payables](../sources/e48761.md) · [e48760](../sources/e48760.md) · [e48763](../sources/e48763.md)
- [f10310 / f10570 / f10312 Receivables](../sources/f10310.md) · [f10570](../sources/f10570.md) · [f10312](../sources/f10312.md)
- [e48771 Subledger Accounting](../sources/e48771.md)
- [e48829 Cost Management（CIC）](../sources/e48829.md)

## Open Questions / 留白

- AGIS 文档（2019 年版）与当前 12.2 补丁的差异（需 MOS）。
- 复杂关联交易（CIC）的完整配置与处理链路（正文待读）。
- 集团内部销售/采购订单场景在 OM/PO 侧的具体配置。
- 企业实例的关联公司关系、账户规则与批号序列（无权限，留白）。

伴随内部订单/实物流的关联开票（CIC）已 T1 化：
[Intercompany Invoicing 与复杂关联交易（CIC）（T1）](../concepts/intercompany-invoicing-t1.md)。
