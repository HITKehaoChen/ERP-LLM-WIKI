---
title: "SLA AMB 账户推导规则（T1）"
type: concept
status: stable
verified: doc-only
sources: [e48771]
updated: 2026-08-04
---

# SLA AMB 账户推导规则（T1）

> 本页为 **T1 官方文档原文**级知识，来源：Oracle Subledger Accounting Implementation Guide（e48771）“Accounting Methods Builder”章。原始快照：[T149412T149415.htm](../../sources/docs/e48771/chapters/T149412T149415.htm)。

## 1. AMB 八步流程（官方）

1. Define Journal Line Types（日记账行类型）
2. Define Journal Entry Descriptions（摘要）
3. Define Mapping Sets（映射集）
4. Define Account Derivation Rules（账户推导规则）
5. Define Supporting References（支持性引用）
6. Define Journal Lines Definitions（日记账行定义）
7. Define Application Accounting Definitions（应用会计定义）
8. Define Subledger Accounting Methods（子账会计方法，可整组分配给账套）

## 2. 交易科目表 vs 会计科目表（Transaction / Accounting CoA）

- **交易科目表**：主账套的科目表，事务录入/维护（如 AR 发票上的弹性域）使用；账户推导规则的来源值取自交易科目表。
- **会计科目表**：生成子账日记账分录所用科目表，取自分录所属账套。
- 主账套中两者**始终相同**；次级账套（secondary ledger / multiple representations）中可不同。
- 未指定时默认用主账套科目表；未指定会计科目表时，除弹性域限定段外不能为单个段定义推导。
- **科目表映射**：多表示场景下，交易科目表→会计科目表的映射在账套级定义；当交易与会计科目表不同且推导规则按整个弹性域取 Source 值时必须有映射；映射要求交易科目表粒度 ≥ 会计科目表（多对一）。

## 3. 映射集（Mapping Sets）

- 类型：整个会计弹性域（Accounting Flexfield）、单个段（Segment）或值集（Value Set）；
- Input Value → Output Value；**Default 值类型**用于来源值未命中任何输入值时，避免创建会计时失败；
- 示例：小企业供应商 Yes→成本中心 100，No→200。

## 4. 账户推导规则（Account Derivation Rules）

- 为特定会计科目表推导账户；可推导**整个弹性域**或**单个段**；
- 值来源：交易对象的 Source 值（交易科目表）、常量、映射集等；
- 同一种推导规则可被多条日记账行定义复用（如 PO 费用行与 PO 应计行都用“从 PO 分配复制账户”的规则）。

### 窗口字段与规则（官方原文）

- **Output Type**：Accounting Flexfield（整个弹性域）、Segment（单段）、Value Set（值集，未指定会计科目表时用于跨科目表复用）。
- **Value Type**：`Source`、`Constant`、`Mapping Set`、`Account Derivation Rule`（引用另一条规则，不能循环引用）。
- **Priority**：数字越小优先级越高，按升序评估直到条件满足；无条件的最后一条明细行作为默认（优先级最低）。某段一旦有合法值即不再覆盖。
- 会计科目表配置限制（官方表）：
  - 科目表未指定（Null）：弹性域规则只能是 Source（整个弹性域或段来源）；值集规则可用 Source/Mapping/Constant。
  - 科目表已指定：弹性域规则可用 Source/Mapping Set/Constant/Account Derivation Rule；段规则可用 Source/Mapping Set/Constant；值集规则不允许。
- **Segment rules**：可从弹性域来源取某段（如从负债弹性域的成本中心段推导）、非弹性域来源（如 Project Number → Project 段）、或弹性域限定段来源。
- **Value Set rules**：来源必须是 Alphanumeric 且非弹性域/限定段；Mapping Set 必须与规则输出值集相同。
- **常量/映射集**必须指定会计科目表；官方示例：映射集 Vendor Category（Manufacturing→01-100-2210-0000，Services→01-200-2210-0000）。
- 官方强烈建议：不改种子规则，复制后修改（Owner=User）；升级可能覆盖种子组件，用 merge analysis 评估影响。

### Account Derivation Rule 的取值逻辑补充

- 整弹性域规则用 Source 时取交易科目表的整个弹性域；次级账套场景需要科目表映射（多对一，交易科目表粒度 ≥ 会计科目表）。
- 会计属性（Accounting Attributes）在事件类级分配来源，可下推到日记账行类型/应用会计定义覆盖；Header/Line 两级。

## 5. 业务流方法（Business Flows：Same Entry / Prior Entry / None）

- **None**：无业务流，行直接由账户推导规则生成。
- **Same Entry**：同一日记账内两侧行共享关键值。
- **Prior Entry**：从业务流上游事件的分录复制值（如采购收货的应计行 → AP 发票的应计行）。
- 官方示例（PO→收货→发票）：
  - 收货事件：PO Charges（DR，None）与 PO Accruals（CR，None，业务流类 Purchased Goods）各按 PO 分配行复制科目生成 4 行；
  - 发票事件：AP Accruals（DR，**Prior Entry**，业务流类 Purchased Goods）从上游收货分录复制科目；AP Inv Liability（CR，None）用独立推导；
  - 结果：采购→收货→发票的应计科目在业务流内保持一致。

## 6. 其他机制

- **事件模型**：会计事件按 Event Entity → Event Class → Event Type 分级；AMB 组件多按事件类/事件类型定义（见 [SLA 成本事件模型（T1）](sla-costing-events.md)）。
- **自定义来源（Custom Sources）**：用 PL/SQL 函数扩展应用会计定义的来源；注意性能影响。
- **复制与修改（Copy and Modify）**：不要直接改种子组件（升级可能覆盖）；复制后修改，Owner=User；自定义组件只能赋给自定义定义；可用 merge analysis 评估升级影响。
- **多表示（Multiple Representations）**：同一子账会计方法可分配给多个账套；次级账套可用不同币种/科目表/日历/会计定义。

## 证据

- e48771 “Accounting Methods Builder”章：https://docs.oracle.com/cd/E26401_01/doc.122/e48771/T149412T149415.htm

## Open Questions

- Account Derivation Rules 窗口的完整字段（值类型枚举、Segment 覆盖规则）正文待逐段整理。
- 企业实例的会计方法/映射集/推导规则（无权限，留白）。
