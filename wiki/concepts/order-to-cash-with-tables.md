---
title: "Order-to-Cash 表级流程（T2 社区资料）"
type: process
status: draft
verified: needs-verification
sources: [community-o2c-pdf]
updated: 2026-08-04
---

# Order-to-Cash 表级流程（T2 社区资料）

> **可信度说明**：本页整理自用户提供的社区培训 PDF（19 页，含各阶段表名、关键列与示例 SQL）。表名/列名与官方一致的可能性高，但**状态码取值与字段含义尚未经 eTRM/实例验证**，标注 T2/T3。
>
> raw 快照：[PDF](../../sources/docs/o2c/Order_to_Cash_O2C_Cycle_with_Table_detail.pdf) · [正文文本](../../sources/docs/o2c/o2c_extract.txt)

## 流程总览

Enter → Book → Pick Release →（Pick Confirm）→ Ship Confirm → Create Invoice（Workflow Background Process → RA 接口 → AutoInvoice）→ Create Receipt → Transfer to GL → Journal Import → Posting。

## 各阶段表与关键列（社区资料）

| 阶段 | 表 | 关键列/状态值（资料所述） |
| --- | --- | --- |
| 1. Order Entry | OE_ORDER_HEADERS_ALL | HEADER_ID、ORG_ID、ORDER_NUMBER、ORDER_TYPE_ID、FLOW_STATUS_CODE（=Entered）、SHIP_FROM/SHIP_TO_ORG_ID、TRANSACTIONAL_CURR_CODE |
| 1. Order Entry | OE_ORDER_LINES_ALL | LINE_ID、HEADER_ID（关联头）、ORDERED_ITEM、INVENTORY_ITEM_ID、PRICING_QUANTITY、ORDERED_QUANTITY、FLOW_STATUS_CODE、UNIT_SELLING_PRICE_PER_PQTY |
| 2. Booking | OE_ORDER_HEADERS_ALL / OE_ORDER_LINES_ALL | 头 FLOW_STATUS_CODE=BOOKED；行 FLOW_STATUS_CODE=AWAITING_SHIPPING |
| 2. Booking | WSH_DELIVERY_DETAILS | DELIVERY_DETAIL_ID、SOURCE_HEADER_ID、SOURCE_LINE_ID、SOURCE_CODE、RELEASED_STATUS（=R Ready to Release）、CUSTOMER_ID、INVENTORY_ITEM_ID、SHIP_FROM/TO_LOCATION_ID、MOVE_ORDER_LINE_ID、REQUESTED/SHIPPED_QUANTITY、SUBINVENTORY、SHIP_METHOD_CODE、CARRIER_ID |
| 2. Booking | WSH_DELIVERY_ASSIGNMENTS / MTL_DEMAND | 插入分配记录；DEMAND INTERFACE PROGRAM 写入 MTL_DEMAND |
| 3. Pick Release | OE_ORDER_LINES_ALL | FLOW_STATUS_CODE=PICKED 或 AWAITING_SHIPPING（依 Auto Pick Confirm） |
| 3. Pick Release | WSH_DELIVERY_DETAILS | RELEASED_STATUS=S（Release to Warehouse）或 Y（Pick Confirmed） |
| 3. Pick Release | WSH_NEW_DELIVERIES / WSH_DELIVERY_ASSIGNMENTS | Auto Create Delivery=Yes 时创建交付并回填 DELIVERY_ID |
| 4. Ship Confirm | WSH_DELIVERY_DETAILS | RELEASED_STATUS=C（Shipped） |
| 4. Ship Confirm | OE_ORDER_LINES_ALL | FLOW_STATUS_CODE=SHIPPED（头仍 BOOKED） |
| 5. Invoice | RA_INTERFACE_LINES_ALL | Workflow Background Process 写入；INTERFACE_LINE_CONTEXT=Order Entry、INTERFACE_LINE_ATTRIBUTE1=订单号、INTERFACE_LINE_ATTRIBUTE3=Delivery ID；随后 AutoInvoice Master/Import 创建发票 |
| 5. Invoice | RA_CUSTOMER_TRX_ALL | 发票头；INTERFACE_HEADER_ATTRIBUTE1=订单号、INTERFACE_HEADER_ATTRIBUTE2=订单类型、TRX_NUMBER=发票号 |
| 5. Invoice | RA_CUSTOMER_TRX_LINES_ALL | 发票行；INTERFACE_LINE_ATTRIBUTE1..14=订单号/订单类型/Delivery/Waybill/Line ID/Picking Line/BOL/仓库/价格调整/装运号/选件号/服务号等 |
| 6. Receipt | AR_CASH_RECEIPTS_ALL | CASH_RECEIPT_ID；收款后 OE_ORDER_LINES_ALL.FLOW_STATUS_CODE=CLOSED |
| 7. Transfer to GL | GL_INTERFACE | General Ledger Transfer Program 写入（调整/退单/贷项/承诺/借项/发票/收款） |
| 8. Journal Import | GL_JE_BATCHES / GL_JE_HEADERS / GL_JE_LINES | Journal Import 从 GL_INTERFACE 导入 |
| 9. Posting | GL_BALANCES | Post 后更新账户余额 |

## 关键状态码速查（资料所述，待验证）

| 位置 | 取值 |
| --- | --- |
| OE_ORDER_HEADERS_ALL.FLOW_STATUS_CODE | Entered → Booked（→ Closed） |
| OE_ORDER_LINES_ALL.FLOW_STATUS_CODE | Entered → Awaiting Shipping → Picked/Awaiting Shipping → Shipped → Closed |
| WSH_DELIVERY_DETAILS.RELEASED_STATUS | R=Ready to Release、S=Release to Warehouse/Submitted、Y=Pick Confirmed、C=Shipped |

> 官方对应关系见 [Shipping 发运状态与流程（T1）](shipping-statuses-and-processes.md) 与 [销售订单生命周期与状态机（T1）](order-lifecycle-and-status.md)；如冲突，以官方文档为准。

## 与知识库其他页的关系

- 状态机：与 T1 页一致（Booked/Awaiting Shipping/Picked/Shipped/Closed）。
- 开票接口：RA 接口表与 AutoInvoice 对应 [销售订单生命周期与状态机（T1）](order-lifecycle-and-status.md) 第 6 节。
- 收款/GL：对应 [Intercompany 域](../domains/intercompany.md) 的 AR/GL 链路。

## 视频实操参考（英文字幕，T2）

来源：YouTube [2mMtLycHK-4](https://www.youtube.com/watch?v=2mMtLycHK-4)（用户提供的 O2C 播放列表首个视频）；自动生成英文字幕，raw 快照：[transcript](../../sources/docs/community/youtube/2mMtLycHK-4.transcript.txt)。

视频演示步骤（摘要）：

1. 用 OM Super User 登录；先到 Inventory 的 On-hand Availability/On-hand Quantity 查物料库存（演示：M1 Seattle Manufacturing，AS5488 Desktop）。
2. 创建销售订单（客户/行物料/数量）。
3. Book 订单。
4. 自动创建 Pick Confirm / Pick Release 发运订单；查看自动生成的**事务与报表**。
5. 从并发程序运行 **Workflow Background Process**（正常后台自动运行），系统自动生成发票。
6. 在 Accounts Receivable 查看发票。

> 抓取方式：`python scripts/fetch_youtube_transcript.py <video_id>`（依赖 `youtube-transcript-api`）；播放列表其余视频可逐个抓取后再整理。

## Open Questions

- 各表字段官方定义（需 eTRM/实例）。
- 状态码取值与官方文档逐项核对。
- 播放列表其余视频的转录与要点（可按需继续抓取）。
