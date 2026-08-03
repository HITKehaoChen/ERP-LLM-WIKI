---
title: 知识库总览
type: overview
status: stable
verified: doc-only
updated: 2026-08-03
---

# Oracle EBS R12.2 标品文档知识库

本知识库把 Oracle EBS R12.2 官方公开文档持续编译成一个相互链接的 Markdown Wiki。目标不是“背下 393 本书”，而是：

1. 全部官方文档进入目录（可检索、可追溯）。
2. 每个业务问题能定位到对应文档与章节。
3. 重点业务域（WIP / Inventory / OM / 关联交易）深入阅读并结构化。
4. 文档没有证明的内容明确留白，等 MOS / 实例权限后再补证。

## 三层结构（Karpathy LLM Wiki 模式）

| 层 | 目录 | 谁维护 | 规则 |
| --- | --- | --- | --- |
| raw 原始素材 | `sources/` | 脚本抓取 | 不可变，LLM 只读 |
| wiki 编译层 | `wiki/` | LLM | 页面互联、带证据、留白标注 |
| schema | `AGENTS.md` | 人 + LLM 共同演进 | 定义约定与 ingest/query/lint |

## 当前覆盖（2026-08-03）

- 全集索引：393 本（367 本已分类，13 本链接失效）。
- 重点文档快照：63 份（62 份 HTML+PDF，1 份仅 PDF）。
- 四大重点域页：WIP、Inventory、Order Management、Intercompany。

## 信任等级

- `T1` 官方文档原文 —— 带来源页与章节引用。
- `T2` 文档归纳 —— 明确标为归纳。
- `T3` 推断/假设 —— 必须标 `⚠ 未验证` 并列入 Open Questions。
- `T4` 实例验证 —— 当前无权限，留白。

## 主要缺口（详见 coverage/report.md）

- My Oracle Support（已知问题、补丁、诊断脚本）不可得。
- eTRM 完整表字段与源码级调用链不可得。
- 企业实例的当前配置与真实行为不可得。

## 使用方式

- 人：用 Obsidian 打开本目录，从 [index.md](index.md) 开始浏览。
- LLM：先读 `AGENTS.md`，再读 [index.md](index.md)；答案必须引用来源页并回写有价值的新知识。
