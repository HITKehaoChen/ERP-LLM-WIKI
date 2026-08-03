# sources/ — raw 层（不可变）

本目录是知识库的原始素材层，**LLM 只读，绝不修改**。刷新由脚本完成：

- `catalog/` — Oracle EBS R12.2 官方文档全集索引（`scripts/fetch_ebs_catalog.py` 生成）：
  - `ebs_r122_booklist.json/.csv`：官方 “Current Booklist”，393 本书，含标题、Part Number、HTML/PDF 链接、描述。
  - `ebs_r122_areas.json`：书单与产品导航分类（technology/financials/scm/vce/…）的映射。
  - `priority_docs.json`：63 份重点文档的元数据与章节树（`scripts/fetch_priority_docs.py` 生成）。
- `docs/<part>/` — 重点文档原始快照：
  - `toc.html` / `title.html`：官方目录页与版权页快照（HTML 可用时）。
  - `<part>.pdf`：HTML 已失效、仅 PDF 可用的文档（如 e48763）。

抓取时间见各 JSON 的 `fetched_at` / `generated_at`。官方总入口：
[Oracle EBS R12.2 Documentation Web Library](https://docs.oracle.com/cd/E26401_01/)
