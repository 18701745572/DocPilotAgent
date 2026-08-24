# 变更日志 (CHANGELOG)

> DocPilotAgent 文档、代码、prompt 版本对齐与追溯。

本项目遵循 [Keep a Changelog](https://keepachangelog.com/) 风格，版本号语义化（SemVer）。

---

## 1. 版本对齐表

> 关键：文档版本、代码版本、prompt 版本需对齐。任何一方变动需在此登记。

| 发布版本 | 文档集版本 | 代码版本 | Prompt 版本 | 发布日期 | 说明 |
|---|---|---|---|---|---|
| v0.1.0-docs | docs-v1 | - | - | 2026-08-24 | 文档先行定稿，11 → 17 份 |
| v0.1.0 | docs-v1 | code-v1 | prompt-v1.0 | 2026-08-24 | 首个可用版本（[ROADMAP](./ROADMAP.md) P0~P7 完成） |

### 版本号约定

| 类型 | 格式 | 谁变化 |
|---|---|---|
| 发布版本 | `vMAJOR.MINOR.PATCH` | 整体发布 |
| 文档集版本 | `docs-vN` | 任一文档变更 |
| 代码版本 | `code-vN` | 代码变更 |
| Prompt 版本 | `prompt-vX.Y` | [PROMPT.md](./PROMPT.md) 变更 |

---

## 2. 变更条目

### [v0.1.0] - 2026-08-24

#### Added（按 [EXECUTION_GUIDE](./EXECUTION_GUIDE.md) P0~P7 顺序实现）
- **P0 项目骨架**：`pyproject.toml`、`.env.example`、`.gitignore`、`src/docpilot/__init__.py`、`config.py`
- **P1 基础设施**：`llm.py`（ChatOpenAI 封装）、`embeddings.py`（OpenAIEmbeddings 封装）、`vectorstore.py`（Milvus Lite 文档/记忆集合）
- **P2 RAG 链路**：`loader.py`（Markdown 加载切分）、`retriever.py`（文档检索）、示例知识库 `docs/api/user-service.md`、`docs/troubleshooting/oom.md`、`logs/app.log`
- **P3 跨会话记忆**：`memory.py` 的 `PersistentMemory`（add/recall/reset，向量化持久化）
- **P4 只读工具白名单**（核心练习点）：`tools/search_docs.py`、`tools/read_file.py`（路径白名单 + 软链防御）、`tools/search_logs.py`、`tools/__init__.py` 的 `ALL_TOOLS`
- **P5 智能体编排**：`agent.py` 含 `SYSTEM_PROMPT`（9 节完整规格）、`build_agent()`、`ask()`（记忆召回 → 注入 → 执行 → 写入）
- **P6 CLI**：`cli.py` 用 Typer + Rich 实现 `index`/`ask`/`reset` 三命令

#### Changed
- 适配 LangChain 1.x：`agent.py` 由 `AgentExecutor/create_tool_calling_agent` 改用 `create_agent`（LangGraph 风格），保留 SYSTEM_PROMPT 与工具白名单不变
- `cli.py` 由占位升级为完整 Typer 应用

#### Security
- 三层防御全部落地：L1 SYSTEM_PROMPT 约束、L2 `ALL_TOOLS` 仅 3 只读工具、L3 `read_file` 路径白名单 + 符号链接检查
- 对抗用例 T-S2/S3/S5/S6 自动化通过（路径穿越、越权读取、软链逃逸、无写工具）
- T-S1/S4（prompt injection）依赖真实 LLM,SYSTEM_PROMPT 已含拒答模板与信号词

#### 验收（依据 [RELEASE.md](./RELEASE.md) §3.1 必查项）
- [x] `python -m compileall src` 通过
- [x] `pip install -e .` 成功，`docpilot --help` 列出三命令
- [x] `docpilot index` 空目录退出码 1，正常目录输出片段数
- [x] 工具白名单断言：`ALL_TOOLS` 恰为 3 个只读工具
- [x] read_file 路径对抗 7 条全过（含软链 UC-S6）
- [x] SYSTEM_PROMPT 内容断言通过
- [x] 文档对齐：config 字段 / ALL_TOOLS / SYSTEM_PROMPT / CLI 接口全部一致
- [ ] 端到端 ask 与跨会话记忆持久化：需真实 OpenAI 兼容 API Key（沙盒无 Key,留人工验证）
- [ ] 兼容接口验证（豆包/DeepSeek）：留人工验证

#### 已知限制（依据 [ROADMAP](./ROADMAP.md) 后续项）
- LLM 行为对抗（T-S1/S4）需真实 API Key 人工评审
- 跨进程记忆持久化测试需真实嵌入服务
- 记忆按 session_id 删除未实现（当前为集合级 drop）
- LangChain 1.x API 与 [DESIGN.md](./DESIGN.md) §3.2 描述的 AgentExecutor 略有差异，已用 `create_agent` 等效替代

### [Unreleased]

#### 文档新增
- 新增 [DEVELOPMENT.md](./DEVELOPMENT.md) 开发者指南
- 新增 [CHANGELOG.md](./CHANGELOG.md) 本文件
- 新增 [DATA_CURATION.md](./DATA_CURATION.md) 知识库运营
- 新增 [RELEASE.md](./RELEASE.md) 发布门禁
- 新增 [adr/](./adr/) ADR 独立归档（含 ADR-001~004 迁入 + ADR-005 新增 + 模板）
- 新增 [EXECUTION_GUIDE.md](./EXECUTION_GUIDE.md) 执行提示词列表（P0~P7 共 30 条）

#### 文档更新
- 更新 [README.md](../README.md) 文档索引：11 → 17 份，新增"工程运营层"与"执行层"
- 更新 [TRACEABILITY.md](./TRACEABILITY.md) 文档主题表与状态汇总

### [v0.1.0-docs] - 2026-08-24

#### 文档新增（首批 11 份）
- [REQUIREMENTS.md](./REQUIREMENTS.md) 需求规格
- [DESIGN.md](./DESIGN.md) 架构设计
- [API.md](./API.md) CLI 接口规范
- [CONFIG.md](./CONFIG.md) 配置说明
- [ROADMAP.md](./ROADMAP.md) 开发路线图
- [PROMPT.md](./PROMPT.md) 智能体行为规范
- [TOOLS.md](./TOOLS.md) 工具规范
- [SECURITY.md](./SECURITY.md) 权限模型
- [EVAL.md](./EVAL.md) 评估策略
- [TEST_PLAN.md](./TEST_PLAN.md) 测试策略
- [TRACEABILITY.md](./TRACEABILITY.md) 追溯矩阵

#### 锁定决策
- 技术栈：Python + LangChain + OpenAI 兼容 + Milvus Lite + Typer
- 三大练习点对应文档：RAG/记忆/权限约束

---

## 3. 变更登记规则

### 3.1 谁需要登记

| 改动类型 | 登记 |
|---|---|
| 任一 `docs/*.md` 改动 | 是 |
| 代码改动 | 是（按 feat/fix/test/refactor 分类） |
| Prompt 改动 | 是 + 同步 [PROMPT.md](./PROMPT.md) §9 版本号 |
| 依赖升级 | 是 + 标注是否 breaking |
| 仅注释/格式 | 否 |

### 3.2 登记位置

- 未发布改动 → `[Unreleased]` 段
- 发布时 → 移入新版本段，填发布日期

### 3.3 变更类型

| 标签 | 含义 |
|---|---|
| Added | 新功能/新文档 |
| Changed | 现有功能/文档调整 |
| Deprecated | 即将移除 |
| Removed | 已移除 |
| Fixed | 修复 |
| Security | 安全相关（必须同步 [SECURITY.md](./SECURITY.md)） |

---

## 4. 与其他文档的联动

| 本文档条目类型 | 必同步的文档 |
|---|---|
| Added 文档 | [README.md](../README.md) 索引 + [TRACEABILITY.md](./TRACEABILITY.md) §4 |
| Changed prompt | [PROMPT.md](./PROMPT.md) §9 + [EVAL.md](./EVAL.md) 回归 |
| Security | [SECURITY.md](./SECURITY.md) + [TEST_PLAN.md](./TEST_PLAN.md) §4 |
| Changed 工具 | [TOOLS.md](./TOOLS.md) + [SECURITY.md](./SECURITY.md) §3 |
| 发布版本 | [RELEASE.md](./RELEASE.md) 发版检查表 |

---

## 5. 版本策略

### 5.1 SemVer 应用

| 位 | 触发 | 示例 |
|---|---|---|
| MAJOR | 不兼容变更（约束松动、CLI 命令删除） | 1.0.0 → 2.0.0 |
| MINOR | 向后兼容新增（新工具、新命令、新文档） | 1.0.0 → 1.1.0 |
| PATCH | 向后兼容修复 | 1.0.0 → 1.0.1 |

### 5.2 文档集版本（docs-vN）

独立于发布版本，每次文档改动 +1，便于追溯"代码基于哪版文档实现"。

### 5.3 预发布

`v0.x.y` 为 1.0 前的预发布，无严格 SemVer 兼容承诺。

---

## 6. 历史回溯

如需查找"某功能何时加入"，按以下顺序：

1. 本文档对应版本段
2. [TRACEABILITY.md](./TRACEABILITY.md) 找实现模块
3. [adr/](./adr/) 找决策背景
4. Git log 找具体提交
