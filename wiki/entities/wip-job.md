---
title: "WIP Job（离散任务）"
type: entity
status: stable
verified: doc-only
sources: [e48905]
updated: 2026-08-04
---

# WIP Job（离散任务）

## 定义

WIP Job 是离散制造的最小执行单元：一份任务 = 装配件 + 数量 + BOM/工艺路线 + 计划起止 + 账户类（WIP Accounting Class）。见 [e48905 · “Overview of Creating Discrete Jobs”](../sources/e48905.md)。

## 任务类型（T2 归纳）

| 类型 | 说明 | 官方章节 |
| --- | --- | --- |
| 标准离散任务 | 按 BOM/工艺路线生产 | [“Defining Discrete Jobs Manually”](../sources/e48905.md) |
| 非标准任务 | 无标准 BOM/工艺，用于维修/杂项 | [“Non-Standard Discrete Jobs”](../sources/e48905.md) |
| 重复性计划 | Repetitive Schedule，按生产线 | [“Overview of Repetitive Manufacturing”](../sources/e48905.md) |
| 流水线计划 | Flow Schedule | [“Flow Schedules”](../sources/e48905.md) |
| 项目任务 | Project Job | [“Project Jobs”](../sources/e48905.md) |

## 生命周期

Unreleased → Released → Complete（→ Complete-No Charges）→ Closed，以及 On Hold / Cancelled 分支。
完整状态定义、转换矩阵与事务控制见 [WIP 任务与重复性计划状态机（T1）](../concepts/wip-job-status-machine.md)。

## 关键属性（T2 归纳）

- 装配件、需求数量、BOM/工艺路线版本
- 计划日期、车间状态（Shop Floor Status）
- 供应类型（Supply Type，如 Push/Pull/倒冲）— [e48905 · “Supply Types”](../sources/e48905.md)
- WIP 账户类（影响科目推导）

## 相关页面

- [WIP 域](../domains/work-in-process.md)
- [离散制造闭环](../processes/discrete-manufacturing-closed-loop.md)
- 来源：[e48905](../sources/e48905.md)
