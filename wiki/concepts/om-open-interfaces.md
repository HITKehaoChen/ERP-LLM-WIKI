---
title: "OM Open Interfaces 与 API（T2 社区转印）"
type: concept
status: draft
verified: needs-verification
sources: [community-oracleebs4u]
updated: 2026-08-05
---

# OM Open Interfaces 与 API（T2 社区转印）

> **可信度说明**：本页内容来自社区博客（oracleebs4u，2015）转印的 Oracle 文档“Open Interfaces, API, and Electronic Messaging Guide”综述，非官方原始来源。表名/API 名可作检索线索，**字段细节与最新版本以官方 iRepository / eTRM / Oracle Integration Repository 为准**。
>
> raw 快照：[HTML](../../sources/docs/community/oracleebs4u-om-open-interfaces.html) · [正文文本](../../sources/docs/community/oracleebs4u-om-open-interfaces.txt) · 原文：[oracleebs4u.blogspot.com](https://oracleebs4u.blogspot.com/2015/08/oracle-order-management-open-interfaces.html)

## 1. 三种集成方式（官方综述）

1. **Interface Tables（接口表）**：外部数据先写接口表，再运行并发程序校验并应用到产品表；可编辑报错记录后重新提交。适合批量。
2. **Interface Views / Business Views（业务视图）**：简化数据关系供报表/导出，如 `OE_ORDER_HEADERS_BV`。
3. **Function Calls / Programmatic Interfaces（API）**：直接调用公共函数实时处理，如 `OE_ORDER_PUB.PROCESS_ORDER`。

> 官方原则：**永远不要直接写产品表**，必须走接口表+并发程序或 API。

## 2. 关键接口清单（社区转印表）

| 接口/API | 方向 | 类型 | 对象 |
| --- | --- | --- | --- |
| Order Import | Inbound | Table | OE_HEADERS_IFACE_ALL、OE_LINES_IFACE_ALL、OE_RESERVTNS_IFACE_ALL、OE_CREDITS_IFACE_ALL、OE_PRICE_ADJS_IFACE_ALL、OE_LOTSERIALS_IFACE_ALL、OE_ACTIONS_IFACE_ALL |
| Process Order | Inbound | Process | OE_ORDER_PUB.PROCESS_ORDER |
| Agreement / Pricing 系列 | In/Out | Procedure | OE_PRICING_CONT_PUB、QP_MODIFIERS_PUB、QP_PRICE_LIST_PUB、QP_PRICE_FORMULA_PUB、QP_LIMITS_PUB、QP_PREQ_PUB、QP_BULK_LOADER_PUB 等（QP_* 大批定价 API） |
| Release Management | Inbound | Table | RLM_INTERFACE_HEADERS、RLM_INTERFACE_LINES |
| Shipping（WSH） | Inbound | Procedure | WSH_TRIPS_PUB、WSH_TRIP_STOPS_PUB、WSH_DELIVERIES_PUB、WSH_EXCEPTIONS_PUB、WSH_DELIVERY_DETAILS_PUB、WSH_CONTAINER_PUB、WSH_FREIGHT_COSTS_PUB、WSH_PICKING_BATCHES_PUB |

## 3. 开放接口的通用组成部分

- **Source Application**：外部系统或 EBS 其他模块，数据来源。
- **Destination Application**：目标应用，接收数据继续处理/存储。
- **Interface Table 列类型**：Identifier Columns（标识来源/目标唯一键）、Control Columns（跟踪每行处理状态）、其余数据列。
- 校验失败可编辑后重交；批次/组 ID 用于控制处理范围。

## 4. 与知识库其他页的关系

- Order Import / HVOP 在 [销售订单生命周期与状态机（T1）](order-lifecycle-and-status.md) 与 [OM 工作流与种子流程（T1）](om-workflow-t1.md) 中出现。
- 接口表字段与业务事件见 [OM 数据模型概览（T1）](om-data-model-t1.md) 与官方 eTRM（权限缺口）。

## Open Questions

- 各接口表字段的官方定义（需 eTRM/iRepository）。
- R12.2 与 2015 转印内容之间的差异（需官方最新文档核对）。
