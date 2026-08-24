# ADR-002: 选择 Milvus Lite 作为向量库

- **状态**：Accepted
- **日期**：2026-08-24
- **决策者**：用户指定 + 项目设计
- **关联**：[DESIGN.md](../DESIGN.md) §1、§4

## 背景

项目需要向量库承载两类数据：
1. 文档索引（`docs/` 切分后向量化）
2. 跨会话记忆（Q&A 历史向量化）

约束：
- 本地运行，不上传
- 无需 Docker / 独立服务
- 练习场景，规模小

## 决策

采用 **Milvus Lite**（`pymilvus` + `milvus-lite`），以本地文件 `data/docpilot.db` 作为存储。

## 备选方案

| 方案 | 优点 | 缺点 |
|---|---|---|
| A. Chroma | pip 装即用，轻量 | 生态较新，复杂查询弱 |
| B. FAISS | 成熟，性能强 | 无持久化管理，需自己处理增删 |
| C. Milvus Lite（**采纳**） | 用户指定；Milvus 生态完整，未来可平滑升级到完整 Milvus | 比 Chroma 略重 |
| D. 完整 Milvus | 功能最全 | 需 Docker，违背"本地无服务"约束 |

## 理由

- 用户明确指定 Milvus
- Milvus Lite 保留 Milvus API，未来若需扩展到完整 Milvus（多机、大规模）可平滑迁移
- 本地文件模式契合练习场景

## 影响

- 依赖：`pymilvus>=2.4` + `milvus-lite>=2.4` + `langchain-milvus>=0.1`
- 连接参数：`connection_args={"uri": <db_path>}`
- 集合管理：`auto_id=True`，`drop_old=False`
- [DATA_CURATION.md](../DATA_CURATION.md) §4.3 重建索引需删除整个 db 文件

## 后续追踪

- 落地位置：`vectorstore.py`
- 验证方式：[TEST_PLAN.md](../TEST_PLAN.md) §3 集成测
- 复盘触发：规模增长（> 10 万片段）或需多机时，评估升级到完整 Milvus
