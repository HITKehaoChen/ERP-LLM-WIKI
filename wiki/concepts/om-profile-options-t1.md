---
title: "OM 关键 Profile 选项（T1）"
type: concept
status: stable
verified: doc-only
sources: [e48842, e48843, e48847, e48905, e48820]
updated: 2026-08-04
---

# OM 关键 Profile 选项（T1）

> 本页为 **T1 官方文档原文**级摘要，来源：e48842 “Order Management Profile Option Descriptions and Settings”章及各产品指南正文（均在本次摄入的 raw 快照中）。完整清单以 e48842 设置章为准。

## 订单录入与客户

| Profile | 官方说明 |
| --- | --- |
| OM: Add Customer | 控制能否用 Add Customer 窗口创建客户/地址/联系人：All / None / Address and Contact only（默认 None）。 |
| OM: Add Customer (Order Import) | 控制 Order Import 时能否创建客户及明细（默认 None）。 |
| OM: Administer Public Queries | 控制哪些职责可创建/更新 OM 窗口中的公共查询。 |
| OM: Apply Automatic Attachments | 控制规则附件是否无需干预自动应用。 |

## 履行/模型/套装

| Profile | 官方说明 |
| --- | --- |
| OM: Allow Model Fulfillment Without Configuration | Yes 时模型行无子行也可放行（默认 No：无子行则等配置）。 |
| OM: Allow Standard ATO Items as PTO/Kit Included Components | Yes 时 Kit 中的 ATO 项按 ATO 履行（默认 No：按标准包含项；Site 级）。 |
| OM: Assign New Set For Each Line | 默认 N（每订单一个 Ship/Arrival Set）；Yes 时每标准/Kit/模型行独立 Set，并定义拆分/ATO/PTO/Hybrid 的分配规则。 |
| OM: Scheduling Role | 控制调度访问：CSR only / Scheduler only / CSR and Scheduler。 |
| OM: Raise Status Change Business Event | Yes 时订单行/头状态变更（含履行、关闭阶段）触发 `oracle.apps.ont.oip.statuschange.update` 业务事件。 |
| OM: Invoice Numbering Method | 控制开票编号方式（如 Delivery 时按交货名接口发票号）。 |

## 信用/开票/附件

| Profile | 官方说明 |
| --- | --- |
| OM: Credit Check Notification Recipient | 信用检查失败通知对象；未设置时通知创建订单的用户。 |
| OM: Show Discount Details on Invoice | Yes 时发票上打印折扣明细（折扣作为独立负数量行，与产品行同一收入账户）。 |
| WSH: Retain ATO Reservations | Yes 时 ATO 欠发保留预留（预留状态 Staged→Unstage，交付行→Backordered），避免重新预留。 |

## 跨模块相关

| Profile | 官方说明 |
| --- | --- |
| WIP: Respond to Sales Order Changes | 启用时配置项在 OM 取消分配，Unreleased 任务自动改 On Hold（e48905）。 |
| WIP: Ignore Zero Quantity Backflush | 控制倒冲数量小于 0.000005 时报错还是处理（四舍五入为零则不生成库存事务）（e48905）。 |
| INV: Allow Expense to Asset Transfer | Yes 时允许费用→资产子库转移/倒冲（e48820）。 |
| TP:INV Transaction Processing Mode | 事务处理模式：On-line / Background / Form level（e48820）。 |

## 证据

- e48842 “Order Management Profile Option Descriptions and Settings”：https://docs.oracle.com/cd/E26401_01/doc.122/e48842/T373258T374215.htm

## 附录：Profile 代码清单（e48842 章节正文，103 个）

```text
OM:Generate Diagnostics for Error Activities, OM:Unit Price Precision Type,
OM:Enforce check for duplicate Purchase Orders, ONT_ADD_CUSTOMER, ONT_ADD_CUSTOMER_OI,
ONT_ADMINISTER_PUBLIC_QUERIES, ONT_HON_ATO_FOR_INC, OE_APPLY_AUTOMATIC_ATCHMT,
ONT_ALLOW_MODEL_FULFILL_WITHOUT_CONFIG, ONT_SET_FOR_EACH_LINE, ONT_ATP_ENGINE,
ONT_OVERRIDE_ATP, ONT_AUTO_INTERFACE_LINES_TO_IB, ONT_OPEN_RELATED_ITEMS,
ONT_AUTO_PUSH_GRP_DATE, ONT_AUTOSCHEDULE, ONT_BYPASS_ATP, ONT_CASCADE_SERVICE,
ONT_CHARGES_FOR_BACKORDERS, ONT_CHARGES_FOR_INCLUDED_ITEM, OE_CHARGING_PRIVILEGE,
ONT_CONFIG_QUICK_SAVE, OE_COMMITMENT_BAL_CHECK, OE_COMMITMENT_SEQUENCING,
ONT_AGENT_ACTION_PROFILE, OE_RESP_FOR_WF_UPGRADE, ONT_CREATE_ACCOUNT_INFORMATION,
ONT_CREDIT_CARD_PRIVILEGES, OE_CC_NTF_RECIPIENT, ONT_FEEDBACK_PROFILE,
ONT_REPORTDEFECT_PROFILE, ONT_DEF_BSA_TRANSACTION_PHASE, ONT_DEFAULT_FULFILLMENT_BASE,
ONT_DEBUG_LEVEL, OE_DEBUG_LOG_DIRECTORY, OE_DEFAULT_BLANKET_ORDER_TYPE,
ONT_DEFAULT_PERSON_ID, ONT_DEF_TRANSACTION_PHASE, ONT_DELAY_TAXING,
ONT_DISCOUNTING_PRIVILEGE, ONT_PANDA_DISPLAY, ONT_EM_INTEG_SOURCES,
ONT_MANDATE_CUSTOMER_EMAIL, ONT_GRP_PRICE_FOR_DSP, ONT_ENABLE_PARTIAL_ACCEPTANCE,
ONT_REPRICING_PREFERENCES, ONT_ENFORCE_DUP_PO, ONT_SHIP_METHOD_FOR_SHIP_SET,
ONT_EST_AUTH_VALID_DAYS, ONT_INCLUDED_ITEM_FREEZE_METHOD, ONT_TAX_CODE_FOR_FREIGHT,
ONT_HONOR_ITEM_CHANGE, OE_ID_FLEX_CODE, ONT_ITEM_VIEW_METHOD,
ONT_LIST_PRICE_OVERRIDE_PRIV, ONT_MODIFY_SEEDED_HOLDS, ONT_NEGATIVE_PRICING,
ONT_NEW_EDI_ACK_FWK, OE_NOTIFICATION_APPROVER, ONT_XML_ACCEPT_STATE,
ONT_LARGE_ORDER_SIZE, ONT_PRESERVE_EXT_CR_BAL, ONT_RMA_MANUAL_MODIFIER,
ONT_SPU_MANUAL_MODIFIER, ONT_PRICE_INCLUDED_ITEM, ONT_POPULATE_BUYER,
ONT_PREVENT_BOOKING, ONT_PRINT_CUSTOMER_EXTN_OBJECT, ONT_PROMOTION_LIMIT_VIOLATION_ACTION,
ONT_QUICK_OE_AUTO_REFRESH, OE_UI_DEFER_PRICING, ONT_RAISE_STATUS_CHANGE_BUSINESS_EVENT,
ONT_ICP_DEFAULT_RECORDS, ONT_RESTRICT_CUST_ITEMS, ONT_RETURN_ITEM_MISMATCH_ACTION,
ONT_RETURN_FULFILLED_LINE_ACTION, ONT_TRANSACTION_PROCESSING, ONT_SALES_ORDER_FORM_REFERENCE,
ONT_UI_RESTRICT_CUSTOMERS, ONT_SCHEDULING_ROLE, ONT_SEND_CHANGED_LINES_PRICING,
ONT_SEND_ISO_NOTIFICATION, OE_RECEIVABLES_DATE_FOR_NONSHIP_LINES, ONT_SHOW_LINE_DETAILS,
ONT_SOURCE_CODE, ONT_USE_CONFIGURATOR, ONT_UNIT_PRICE_PRECISION_TYPE, ONT_SHOW_CANCEL_LINES,
ONT_VIEW_CLOSED_LINES, ONT_CONSIDER_TAX_FRT_BSA_AMT, OE_NO_ERROR_MESSAGES,
OE_NO_ERRORED_ACTIVITIES, ONT_CONC_MSG, OE_WF_ACTIVITY_ERROR, OE_WF_ACTIVITY_UNEXP_ERROR,
OE_WF_CONCAT_LINE, OE_WF_CONCAT_RETURN_LINE, OE_RETRY_SUCCESSFUL, OE_EM_NO_WF,
OE_HEADERS_EXT_IFACE_ALL, OE_LINES_EXT_IFACE_ALL, OE_ORDER_HEADERS_ALL_EXT_B,
OE_ORDER_LINES_ALL_EXT_B
```

## 附录 2：默认值与必填（官方表）

e48842 “Profile Options” 官方表共 154 行（OM 及跨应用 Profile），已导出为机器可读 CSV：[sources/catalog/om_profile_defaults.csv](../../sources/catalog/om_profile_defaults.csv)（列：profile / required / default_value / category）。

关键默认值摘录（T1）：

| Profile | 必填 | 默认值 |
| --- | --- | --- |
| OM: Administer Public Queries | Req | No |
| OM: Allow Model Fulfillment Without Configuration | Opt | No |
| OM: Apply Automatic Attachments | Opt | Yes |
| OM: Automatically Interface Lines to IB on Fulfillment | Opt | Yes |
| OM: Cascade Service | Opt | Null ≈ Yes |
| OM: Commitment Sequencing | Opt | No |
| OM: Configuration Quick Save | Opt | No |
| OM: Debug Level | Opt | 0 |
| OM: Default Line Type from Model | Req | Yes |
| OM: Display Actions Button vs. Pop list | Req | Button |
| OM: Enforce Check For Duplicate Purchase Order | Req | Yes |
| OM: Invoice Numbering Method | Req | Automatic |
| OM: Orders Archival / Purge Per Commit | Opt | 100 / 100 |
| OM: Over / Under Shipment Tolerance、Over / Under Return Tolerance | Req | 0 |
| OM: Party Totals Currency | Req | US Dollars |
| OM: Preserve External Credit Balances | Req | Yes |
| OM: Price Included Items | Opt | Yes |
| OM: Send Changed Lines to Pricing | Opt | Yes |
| OM: Source Code | Req | ORDER ENTRY |
| OM: Use Configurator | Opt | Yes |
| OM: View Cancel Lines / View Closed Lines | Opt | Yes / Yes |

## Open Questions

- 全部 Profile 的完整清单与默认值（e48842 章节正文）。
- 企业实例的 Profile 值（无权限，留白）。
