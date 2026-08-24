# 架构决策记录 (ADR)

> DocPilotAgent 的关键架构决策归档。

ADR 用于记录"为什么这么选"，与 [DESIGN.md](../DESIGN.md)（"选了什么"）互补。每条 ADR 不可变；决策变更时新增 ADR 并标记前序被取代。

## 索引

| 编号 | 标题 | 状态 | 日期 |
|---|---|---|---|
| [ADR-001](./0001-tool-allowlist-over-prompt.md) | 工具白名单优于纯提示词约束 | Accepted | 2026-08-24 |
| [ADR-002](./0002-milvus-lite.md) | 选择 Milvus Lite 作为向量库 | Accepted | 2026-08-24 |
| [ADR-003](./0003-vectorized-memory.md) | 跨会话记忆向量化而非全量保留 | Accepted | 2026-08-24 |
| [ADR-004](./0004-path-allowlist.md) | read_file 采用路径白名单 | Accepted | 2026-08-24 |
| [ADR-005](./0005-docs-first.md) | 文档先行，代码后置 | Accepted | 2026-08-24 |

## 模板

新建 ADR 复制 [0000-template.md](./0000-template.md)。

## 状态流转

```
Proposed → Accepted → (Deprecated / Superseded)
```

- **Proposed**：提案
- **Accepted**：采纳，已落地或待落地
- **Deprecated**：弃用，不再推荐
- **Superseded**：被新 ADR 取代，需在新 ADR 中引用本 ADR 编号
