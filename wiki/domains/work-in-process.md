---
title: "Work in Process（WIP）"
type: domain
status: draft
verified: doc-only
sources: [e48905, e48954, e48829, e48906, e48944, e48953, e48907, e53484, e48939, e48959, e48961, e48945, e48947]
updated: 2026-08-04
---

# Work in Process（WIP）

## 一句话定位

WIP 是离散/重复/流水制造的**执行层**：承接 BOM 与工艺路线，管理任务（Job/Repetitive Schedule）从创建、发放、投料、工序移动、完工入库到成本归集的整个生命周期。

> 本文档当前为 **T2 文档归纳**：内容来自官方文档章节结构，尚未逐章阅读正文，也未做实例验证。章节名均可在来源页核对。

## 在供应链闭环中的位置

```mermaid
flowchart LR
    Item[物料主数据] --> BOM[BOM] --> WIP[WIP 任务] --> Issue[物料发放] --> Move[工序移动] --> Cpl[完工入库] --> Cost[成本核算] --> GL[会计分录]
```

完整说明见 [离散制造闭环](../processes/discrete-manufacturing-closed-loop.md)。

## 核心对象

- [WIP Job（离散任务）](../entities/wip-job.md) — 标准任务/非标准任务/重复性计划/流水线计划
- 工艺路线与工序（Operation）— [e48905 · “Overview of Routings and Operations”](../sources/e48905.md)
- 资源（Resource）— [e48905 · “Resource Management”](../sources/e48905.md)
- Shop Floor Status（车间状态）— [e48905 · “Shop Floor Statuses”](../sources/e48905.md)
- WIP Accounting Class — [e48905 · “WIP Accounting Classes”](../sources/e48905.md)

## 主流程（按官方章节归纳）

1. **创建任务**：手工定义（[“Defining Discrete Jobs Manually”](../sources/e48905.md)）、系统自动创建（[“AutoCreating Final Assembly Orders”](../sources/e48905.md)）、接口导入（[“Importing Jobs and Schedules”](../sources/e48905.md)）。
2. **发放**：[“Releasing Discrete Jobs”](../sources/e48905.md)；发放后车间才能执行事务。
3. **物料控制**：组件需求（[“Adding and Updating Material Requirements”](../sources/e48905.md)）、预留、拣料与发料/退料（[“Component Issues and Returns”](../sources/e48905.md)）、倒冲（[“Backflush Transactions”](../sources/e48905.md)）。
4. **工序移动**：[“Move Transactions”](../sources/e48905.md)、完工/返回规则（[“Move Completion/Return Rules”](../sources/e48905.md)）。
5. **资源事务**：[“Resource Transactions”](../sources/e48905.md)；外协见 [“Outside Processing”](../sources/e48905.md)。
6. **完工入库**：[“Assembly Completions and Returns”](../sources/e48905.md)，入库后进入 Inventory。
7. **任务关闭/清理**：[“Closing Discrete Jobs”](../sources/e48905.md)、[“Purging Discrete Jobs”](../sources/e48905.md)。
8. **成本核算**：[“Work in Process Costing”](../sources/e48905.md) + [e48829 Cost Management](../sources/e48829.md)。

物料控制/倒冲/完工入库规则已 T1 化：[WIP 物料控制与完工（T1）](../concepts/wip-material-control-and-completions.md)。

## 任务状态（T1）

完整状态定义、官方转换矩阵与按状态的事务控制见
[WIP 任务与重复性计划状态机（T1）](../concepts/wip-job-status-machine.md)。

## 与 Inventory / OM 的接口点

- 销售订单 → 任务：官方章节 [“Linking Sales Orders and Discrete Jobs”](../sources/e48905.md)、Back-to-Back/ATO 见 [Order Management](order-management.md)。
- 任务 → 库存：完工入库、发料/退料，事务进入 Inventory 体系（见 [Inventory](inventory.md)）。
- 成本 → 财务：WIP 事务经 SLA 生成分录（见 [Intercompany / 财务域](intercompany.md) 与 [SLA 概念](../concepts/subledger-accounting.md)）。

## 相关文档

- [e48905 Work in Process User's Guide](../sources/e48905.md)
- [e48954 Bills of Material User's Guide](../sources/e48954.md)
- [e48829 Cost Management User's Guide](../sources/e48829.md)
- [e48906 MES for Discrete Manufacturing](../sources/e48906.md)
- [e48944 Shop Floor Management](../sources/e48944.md)
- [e48953 Outsourced Manufacturing](../sources/e48953.md)
- [e48907 Flow Manufacturing](../sources/e48907.md)
- [e48939 Engineering](../sources/e48939.md)
- [e48959 / e48961 Quality](../sources/e48959.md) · [e48961](../sources/e48961.md)
- [e48945 / e48947 Manufacturing Operations Center](../sources/e48945.md) · [e48947](../sources/e48947.md)
- [e53484 In-Memory Cost Management](../sources/e53484.md)

## Open Questions / 留白

- 各事务类型对应的**库存/总账账户推导规则**（需读正文 + 实例验证）。
- 任务状态转换的**完整规则表**。
- 当前企业实例中 WIP 参数、账户类、状态码的实际配置（无权限，留白）。
- 表名/字段（如 `WIP_DISCRETE_JOBS`）与事务接口明细（需 eTRM/实例）。
