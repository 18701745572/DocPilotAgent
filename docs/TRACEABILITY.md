# 追溯矩阵 (TRACEABILITY)

> 需求 → 模块 → 命令 → 阶段 → 测试 → 评测 的双向追溯。

改任何一处前先查本表评估影响面。

---

## 1. 需求 → 实现 → 验证

| 需求 ID | 需求摘要 | 实现模块 | CLI 命令 | 阶段 | 测试 | 评测 |
|---|---|---|---|---|---|---|
| FR-1.1 | 递归扫描 .md | loader.py | index | P2 | T-loader-1 | - |
| FR-1.2 | Markdown 切分 | loader.py | index | P2 | T-loader-2 | - |
| FR-1.3 | 写入文档集合 | vectorstore.py | index | P2 | T-index-1 | - |
| FR-1.4 | 增量重建（覆盖） | vectorstore.py | index | P2 | T-index-2 | - |
| FR-2.1 | 问答全链路 | agent.py | ask | P5 | T-agent-1 | D1/D2 |
| FR-2.2 | 引用来源 | agent.py + PROMPT | ask | P5 | T-cite-1 | D4 |
| FR-2.3 | 工具调用 | agent.py | ask | P5 | T-agent-2 | - |
| FR-3.1 | 文档源 | loader/retriever | - | P2 | - | - |
| FR-3.2 | 日志源 | tools/search_logs | - | P4 | T-tool-logs | - |
| FR-3.3 | 文件读取 | tools/read_file | - | P4 | T-tool-read | - |
| FR-4.1 | 记忆向量化 | memory.py | ask | P3 | T-mem-1 | - |
| FR-4.2 | 语义召回 | memory.py | ask | P3 | T-mem-2 | - |
| FR-4.3 | 跨进程持久 | memory.py + Milvus | - | P3 | T-mem-3 | - |
| FR-4.4 | 会话隔离 | memory.py | - | P3 | T-mem-4 | - |
| FR-4.5 | 清空 | memory.py | reset | P3 | T-mem-5 | - |
| FR-5.1 | index 命令 | cli.py | index | P6 | T-cli-1 | - |
| FR-5.2 | ask 命令 | cli.py | ask | P6 | T-cli-2 | - |
| FR-5.3 | --verbose | cli.py | ask -v | P6 | T-cli-3 | - |
| FR-5.4 | reset 命令 | cli.py | reset | P6 | T-cli-4 | - |
| FR-5.5 | --help | cli.py | --help | P6 | T-cli-5 | - |

---

## 2. 非功能需求 → 防御 → 对抗测试

| NFR | 摘要 | 防御层 | 对抗用例 | 文档 |
|---|---|---|---|---|
| NFR-1 | 不可修改代码 | L1+L2 | T-S1, T-S4, T-S5 | [SECURITY §3](./SECURITY.md) |
| NFR-2 | 路径白名单 | L3 | T-S2, T-S3, T-S6 | [SECURITY §3](./SECURITY.md), [TOOLS §2.4](./TOOLS.md) |
| NFR-3 | OpenAI 兼容 | 配置层 | 切豆包/DeepSeek 验证 | [CONFIG §3](./CONFIG.md) |
| NFR-4 | Milvus Lite | vectorstore | 集成测 | [DESIGN §4](./DESIGN.md) |
| NFR-5 | Python ≥ 3.10 | pyproject | CI 矩阵 | - |
| NFR-6 | 数据本地 | 全栈 | - | [SECURITY §1](./SECURITY.md) |
| NFR-7 | 可观测 | --verbose | T-cli-3 | - |
| NFR-8 | 健壮降级 | handle_parsing_errors | T-agent-err | - |

---

## 3. 练习点 → 落地证据

| 练习点 | 需求 | 模块 | 文档 | 测试 |
|---|---|---|---|---|
| RAG + 多数据源 | FR-1, FR-3 | loader/retriever/tools | [DESIGN](./DESIGN.md) §3.1, [TOOLS](./TOOLS.md) | 集成测 |
| 记忆管理 | FR-4 | memory.py | [DESIGN](./DESIGN.md) §3.2, ADR-3 | T-mem-* |
| 输出权限约束 | NFR-1/2 | tools/ + SYSTEM_PROMPT | [SECURITY](./SECURITY.md), [PROMPT](./PROMPT.md) §3, [TOOLS](./TOOLS.md) §0 | T-S1~S6 |

---

## 4. 文档 → 主题

| 文档 | 主题 | 主要服务对象 |
|---|---|---|
| [REQUIREMENTS](./REQUIREMENTS.md) | 做什么 | 所有人 |
| [DESIGN](./DESIGN.md) | 怎么做 | 开发者 |
| [API](./API.md) | 怎么用 | 用户 |
| [CONFIG](./CONFIG.md) | 怎么配 | 运维/用户 |
| [ROADMAP](./ROADMAP.md) | 何时做 | PM/开发者 |
| [PROMPT](./PROMPT.md) | 智能体怎么说话 | 开发者/评审 |
| [TOOLS](./TOOLS.md) | 智能体有什么手 | 开发者 |
| [SECURITY](./SECURITY.md) | 边界在哪 | 评审/安全 |
| [EVAL](./EVAL.md) | 好不好 | 评审 |
| [TEST_PLAN](./TEST_PLAN.md) | 怎么验 | 开发者/CI |
| [TRACEABILITY](./TRACEABILITY.md) | 改一处影响哪 | 维护者 |
| [DEVELOPMENT](./DEVELOPMENT.md) | 怎么开发 | 开发者 |
| [DATA_CURATION](./DATA_CURATION.md) | 知识库怎么养 | 内容 owner |
| [CHANGELOG](./CHANGELOG.md) | 改了什么 | 所有人 |
| [RELEASE](./RELEASE.md) | 怎么发版 | 维护者 |
| [adr/](./adr/README.md) | 为什么这么选 | 评审/维护者 |

---

## 5. 变更影响速查

> 改某文档/模块前,必看的关联点。

| 变更点 | 必查 |
|---|---|
| SYSTEM_PROMPT | [PROMPT](./PROMPT.md) → [SECURITY](./SECURITY.md) §4 → [EVAL](./EVAL.md) D3 → [TEST_PLAN](./TEST_PLAN.md) §4 |
| 新增工具 | [TOOLS](./TOOLS.md) → [SECURITY](./SECURITY.md) §3 → [TEST_PLAN](./TEST_PLAN.md) §2.2 |
| 环境变量 | [CONFIG](./CONFIG.md) → [API](./API.md) §4 → [DESIGN](./DESIGN.md) §4 |
| CLI 命令 | [API](./API.md) → [ROADMAP](./ROADMAP.md) 对应阶段 → [TEST_PLAN](./TEST_PLAN.md) §5 |
| 记忆策略 | [DESIGN](./DESIGN.md) ADR-3 → [PROMPT](./PROMPT.md) §5 → [EVAL](./EVAL.md) |

---

## 6. 状态汇总（截至文档定稿）

| 项 | 状态 |
|---|---|
| 需求条目数 | 5 FR 组 + 8 NFR |
| 对抗用例 | 6 条（T-S1~S6） |
| 评测维度 | 4 类 |
| 文档数 | 16 份（顶层）+ ADR 子目录 7 份 |
| 决策记录 | 5 条 ADR（[adr/](./adr/README.md)） |
| 实现 | 未开始（待按 [ROADMAP](./ROADMAP.md) P0 启动） |
| 文档集版本 | docs-v1（见 [CHANGELOG](./CHANGELOG.md)） |
