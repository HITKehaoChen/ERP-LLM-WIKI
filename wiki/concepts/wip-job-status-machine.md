---
title: "WIP 任务与重复性计划状态机（T1）"
type: concept
status: stable
verified: doc-only
sources: [e48905]
updated: 2026-08-04
---

# WIP 任务与重复性计划状态机（T1）

> 本页为 **T1 官方文档原文**级知识，来源：Oracle Work in Process User's Guide（e48905）第 “Job and Repetitive Schedule Statuses” 章。原始快照：[T228107T228119.htm](../../sources/docs/e48905/chapters/T228107T228119.htm)，官方 URL：https://docs.oracle.com/cd/E26401_01/doc.122/e48905/T228107T228119.htm

## 1. 状态分类

状态分为**用户控制状态**（用户可改，或由事件自动更新）与**处理状态**（由并发程序进度/结果自动更新）：

- 处理状态示例：Pending Bill Load、Pending Routing Load、Failed Bill Load、Failed Routing Load（任务 BOM/工艺并发加载的进度）、Pending Close、Failed Close（任务关闭流程）、Pending-mass loaded（重复性计划从接口/计划员工作台实现）。

## 2. 离散任务（Discrete Job）状态定义

| 状态 | 官方定义（摘要） |
| --- | --- |
| Released | 可生产、可做事务；改为该状态时 release date 自动设为当天，若有工艺路线则任务数量移动到首道工序的 Queue intraoperation 步骤。 |
| Unreleased | 未发放，可更新但不可做事务；仅当无净发料/移动/资源/完工/报废费用、且无关联 PO/PR 时可改回。 |
| Complete | 已完成但**仍接受事务与费用**；完工入库数量等于任务数量时自动更新；只能在更新任务时手工指定。 |
| Complete-No Charges | 完成且不再接受任何活动；不可更新/不可做事务，但可改回 Complete；只能在更新时手工指定。 |
| On Hold | 可更新但不可做事务；可在定义任务时指定。 |
| Cancelled | 完成前取消；不可更新/不可做事务，但可改状态；只能在更新时手工指定。 |
| Closed | 已关闭且不再接受活动；任务关闭流程成功后自动更新；若完成所在会计期间仍开放且功能安全允许，可改回其他状态。 |

## 3. 重复性计划（Repetitive Schedule）状态定义

| 状态 | 官方定义（摘要） |
| --- | --- |
| Released | 可生产、可做事务；若有工艺路线则总装配数量移动到首道工序 Queue 步骤。 |
| Unreleased | 未发放，可更新但不可做事务。 |
| Complete | 完成但仍接受事务；完工数=计划总量且**该装配在该生产线上无后续计划**时自动更新。 |
| Complete-No Charges | 完成且不再接受活动；若存在后续计划（Unreleased 且在自动释放天数内，或 Released/Complete/On Hold）则当前计划自动置为此状态；多余物料可自动滚入后续计划或作为差异。 |
| On Hold | 可更新但不可做事务。 |
| Cancelled | 完成前取消；多余物料可退回库存或滚入后续计划，否则期间关闭时记为差异。 |
| Pending-mass loaded | 由 Open Job/Schedule Interface 或计划员工作台实现；可按 Unreleased 更新但不可做事务；可实现为 Unreleased/Released/On Hold。 |

## 4. 状态转换矩阵（官方原文）

“Change To” 列 × “From” 行；Yes=允许，No=禁止，Cond=有条件，N/A=不适用。

| From \ To | Unreleased | Released | Complete | Complete-No Charges | On Hold | Cancelled | Closed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Unreleased | N/A | Yes | Yes | No | Yes | Yes | Yes |
| Released | Cond | N/A | Yes | No | Yes | Yes | Yes |
| Complete | Cond | Yes | N/A | Yes | Yes | Yes | Yes |
| Complete-No Charges (DIS) | No | No | Yes | N/A | No | No | Yes |
| Complete-No Charges (REP) | No | No | No | N/A | No | No | N/A |
| On Hold (DIS) | Cond | Yes | Yes | No | N/A | Yes | Yes |
| On Hold (REP) | Cond | Yes | Yes | No | N/A | Yes | Yes |
| Cancelled (REP) | No | No | No | No | No | N/A | N/A |
| Cancelled (DIS) | Cond | Yes | Yes | Yes | Yes | N/A | Yes |
| Pending-mass loaded (REP) | Yes | Yes | Yes | No | Yes | Yes | N/A |
| Pending Bill Load (DIS) | No | No | No | No | No | No | No |
| Failed Bill Load (DIS) | Yes | Yes | No | No | Yes | No | Yes |
| Pending Routing Load (DIS) | No | No | No | No | No | No | No |
| Failed Routing Load (DIS) | Yes | Yes | No | No | Yes | No | Yes |
| Pending Close (DIS) | Cond | Yes | Yes | Yes | Yes | Yes | Yes |
| Failed Close (DIS) | Yes | Yes | Yes | No | Yes | Yes | Yes |
| Closed (DIS) | Yes | Yes | Yes | No | No | No | N/A |

官方给出的条件示例：
- Released → Unreleased：仅当无净 issue/move/resource/completion/scrap 费用时允许。
- 不能“反关闭”链接到销售订单的任务，或已在已关闭会计期间内关闭的任务。

## 5. 按状态的事务控制（Transaction Control By Status）

| 事务 | 规则（官方原文） |
| --- | --- |
| 发料/完工/移动/报废/资源 | Released 或 Complete 状态可执行；倒冲与间接费用由来源事务状态间接控制。 |
| 成本更新 | 标准离散任务与非标准资产任务：Unreleased、Released、Complete、Complete-No Charges、On Hold。 |
| 期间关闭 | 重复性计划按 Released/Complete/Complete-No Charges/On Hold（取决于 WIP Recognize Period Variances 参数）自动生成会计事务；非标准费用任务按 Unreleased/Released/Complete/Complete-No Charges/On Hold 生成。 |
| 任务关闭 | 除 Closed、Pending Close、Pending Bill Load、Pending Routing Load 外均可关闭。 |
| 清理（Purge） | 只能清理在已关闭期间关闭的任务；重复性计划清理 Complete-No Charges 与 Cancelled 且期间已关闭。 |

## 6. 其他状态控制

- **发放控制**：Unreleased → Released 时自动设置发放日期并把数量移动到首道工序 Queue 步骤；无净费用时可 Unrelease。
- **Hold 控制**：可手工改为 On Hold；若 WIP Respond to Sales Order Changes 参数启用，配置项在 OM 中取消分配时，Unreleased 任务自动改为 On Hold。
- **ECO 控制**：Engineering 自动对 Unreleased 任务、Unreleased/Released/On Hold 计划实施 Release/Schedule/Implement 状态 ECO；非标准任务不实施。
- **计划控制**：计划产品包含 Unreleased/Released/Complete/On Hold 任务的供应与需求。
- **报表控制**：Closed、Complete-No Charges、Cancelled 任务不列入缺料报表等。
- **字段更新控制**：Closed/Complete-No Charges/Cancelled/处理中状态不可更新；Unreleased/Released/On Hold/Complete 可更新（Class 仅 Unreleased 可改；BOM/工艺引用/版本仅 Unreleased 可改）。

## 7. 证据与 Open Questions

证据：e48905 “Job and Repetitive Schedule Statuses” 章（含 Discrete Job Status Control 字段矩阵、状态转换矩阵、Transaction Control By Status）。

- 状态转换“Cond”条件的**完整展开**（除文中示例外）待逐条核对。
- 实例中任务状态自定义、账户类与状态组合（无权限，留白）。

## 相关页面

- [WIP Job（实体）](../entities/wip-job.md)
- [WIP 域](../domains/work-in-process.md)
- [离散制造闭环](../processes/discrete-manufacturing-closed-loop.md)
