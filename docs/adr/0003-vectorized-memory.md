# ADR-003: 跨会话记忆向量化而非全量保留

- **状态**：Accepted
- **日期**：2026-08-24
- **决策者**：项目设计
- **关联**：[DESIGN.md](../DESIGN.md) ADR-3、[PROMPT.md](../PROMPT.md) §5、[REQUIREMENTS.md](../REQUIREMENTS.md) FR-4

## 背景

[REQUIREMENTS.md](../REQUIREMENTS.md) FR-4 要求跨会话记忆。朴素方案是把全部历史问答塞入 prompt，但：
- 上下文窗口有限（如 128k 也撑不住长会话）
- 长历史噪声大，反而干扰回答
- 跨进程重启需持久化

## 决策

每轮 Q&A 向量化后存入 Milvus 记忆集合（`kb_memory`）。新问题到达时：
1. 用问题向量检索记忆集合 top-3（默认）
2. 仅将相关片段注入 SYSTEM_PROMPT 的 `{memory}` 槽位
3. 不全量保留历史

## 备选方案

| 方案 | 优点 | 缺点 |
|---|---|---|
| A. 全量历史塞入 prompt | 简单；保序 | 窗口爆炸；噪声大 |
| B. 向量化召回（**采纳**） | 窗口可控；语义相关 | 损失时序信息 |
| C. 摘要压缩 | 兼顾长度与上下文 | 摘要质量依赖 LLM；实现复杂 |
| D. B + 时间戳元数据排序 | 兼顾相关与时序 | 实现稍复杂（[ROADMAP](../ROADMAP.md) 后续） |

## 理由

- 窗口可控是硬约束
- 语义相关性比时序更重要（"上次那个问题"通常指最近相关项）
- 向量化天然支持持久化（写入 Milvus 即跨进程）

## 影响

- 记忆集合 `kb_memory` 与文档集合 `kb_docs` 分离
- [PROMPT.md](../PROMPT.md) §5 定义 `{memory}` 注入槽位
- 召回 top_k=3（[CONFIG.md](../CONFIG.md) 未暴露为环境变量，硬编码于 `memory.py`，后续可配置化）
- [ROADMAP.md](../ROADMAP.md) 后续项：按 session_id 删除单会话记忆（当前为集合级 drop）

## 后续追踪

- 落地位置：`memory.py`
- 验证方式：[TEST_PLAN.md](../TEST_PLAN.md) §3.2 记忆持久化测试
- 复盘触发：召回质量不佳时考虑 D 方案（加时间戳）
