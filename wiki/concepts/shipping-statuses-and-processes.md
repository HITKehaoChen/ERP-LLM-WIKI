---
title: "Shipping 发运状态与流程（T1）"
type: concept
status: stable
verified: doc-only
sources: [e48847]
updated: 2026-08-04
---

# Shipping 发运状态与流程（T1）

> 本页为 **T1 官方文档原文**级知识，来源：Oracle Shipping Execution User's Guide（e48847）。原始快照：
> - 交付行状态 [T414830T414838.htm](../../sources/docs/e48847/chapters/T414830T414838.htm)
> - 拣货 [T414830T414840.htm](../../sources/docs/e48847/chapters/T414830T414840.htm)
> - Ship Confirm [T414830T414841.htm](../../sources/docs/e48847/chapters/T414830T414841.htm)
> - LPN [T414830T414839.htm](../../sources/docs/e48847/chapters/T414830T414839.htm)

## 1. 交付行状态（Delivery Line Statuses，官方定义）

| 状态 | 官方定义 |
| --- | --- |
| Not Applicable | 可开票但不可发运的行（如服务行/质保行）。 |
| Not Ready to Release | 不可拣货发放；手工 Import Delivery Line 进入 Shipping 但尚未到 Awaiting Shipping 活动，未排程、无预留。 |
| Ready to Release | 可拣货发放；订单行已到达 Awaiting Shipping 活动（已预订、已排程、已在 Shipping）。只有该状态的行参与 Pick and Ship / Pick, Pack, and Ship。 |
| Released to Warehouse | 拣货发放已处理：已建 Move Order 头/行、找到可用量并创建分配；未 Pick Confirm。 |
| Planned for Crossdocking | WMS 组织在拣货发放时识别到越库供应并已拣货发放。 |
| Staged/Pick Confirmed | 已拣货确认，物料从存储子库移到暂存子库；OM 行状态显示 Picked；Ship Confirm 前保持暂存。 |
| Backordered | 拣货发放找不到全部数量；或 Ship Confirm 时发货量小于请求量、整单欠发、预留转循环盘点等。 |
| Shipped | 已 Ship Confirm 并记为在途；OM/INV 接口尚未完成或延迟。 |
| Interfaced | 已发货且 OM Interface 与 Inventory Interface 并发程序完成（非 OM 来源只需 Inventory Interface）。 |
| Cancelled | （原文后续）已取消。 |

## 2. Pick Release（拣货发放）

- 为订单行生成 Move Order（一行一 Move Order 行），含物料、数量、暂存目的地与来源子库/货位。
- 明细分配（Detailing）：分配后行状态为 **Released to Warehouse**；可自动明细（auto-detailing）或延迟手工明细。
- Pick Confirmation：
  - 执行子库间转移，把物料从源位置移到暂存位置；把高层预留转为含批次/子库/货位的分配预留；
  - 已确认数量 → `Staged/Pick Confirmed`；未确认数量 → `Backordered`；
  - Auto Allocate 与 Auto Pick Confirm 同时为 Yes 时才自动执行；WMS 组织必须手工 Pick Confirm；
  - 少拣时拆行：原行按已拣数量进入 Staged/Pick Confirmed，新行按差额进入 Backorder。
- Overpicking：可超拣至超发容差；超拣数量生成请求量为零的交付行；相关错误 `WSH_REQ_ZERO_INSIDE_ERROR` / `WSH_REQ_ZERO_OUTSIDE_ERROR`。

## 3. Ship Confirm（装运确认）

前置条件：
- 交付行必须 `Staged/Pick Confirmed`；
- 交付必须 Open；
- 至少一行已分配到该交付；
- WMS 组织发货量字段禁用（除非不可预留/不可事务物料）。

选项（Confirm Delivery 窗口）：

| 选项 | 行为 |
| --- | --- |
| Ship Entered Quantities, Unspecified Quantities Ship | 按录入量发货，空白视为全量发货。 |
| Ship Entered Quantities, Unspecified Quantities Backorder | 按录入量发货，空白视为全量欠发。 |
| Ship Entered Quantities, Unspecified Quantities Stage | 未指定行留在暂存并移出交付。 |
| Ship Entered Quantities, Unspecified Quantities Cycle Count | 空白量欠发并把预留转循环盘点。 |
| Ship All | 无视录入量，整单全发。 |
| Backorder All | 整单全欠发。 |

- 校验：发货组织地点/组织的发运日历、客户的接收日历、承运商日历。
- Material Status 校验失败时：Roles 定义为 Warning → 该交付行移出交付并保持 Staged；定义为 Error → 整个交付不能 Ship Confirm。
- 欠发时 ATO 行被拆分且预留丢失（可用 `WSH: Retain ATO Reservations`=Yes 保留）；标准行可用 “Retain Reservations for Standard Items” 参数保留预留。
- Ship Confirm 时可自动创建 Trip/Stops；Contents Firm 的 Trip 保持交付与容器分配，未 Firm 则拆包容器。

## 4. LPN / 容器状态

- WMS 生成的 LPN 在 Shipping 中可见状态：`Staged/Pick Confirmed`、`Loaded to Dock`、`Loaded in Staging`。
- Auto-pack：按 Container-Item 关系与 Percent Fill Basis=Quantity 打包；Auto-pack Master 一次把明细 LPN 装入母 LPN。

## 5. 与 OM 的接口

- 拣货确认后 OM 行状态显示 `Picked`；Ship Confirm 后 OM/INV 接口完成则交付行状态 `Interfaced`。
- 相关流程链：Ready to Release → Released to Warehouse → Staged/Pick Confirmed → Shipped/Backordered → Interfaced。

## Open Questions

- “Cancelled” 状态完整定义与触发条件（正文后续段落待整理）。
- Ship Confirm 的自动流程（Auto Ship Confirm、Release Rule）细节。
- 企业实例的发运参数与角色配置（无权限，留白）。
