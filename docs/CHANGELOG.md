# 变更日志 (CHANGELOG)

> DocPilotAgent 文档、代码、prompt 版本对齐与追溯。

本项目遵循 [Keep a Changelog](https://keepachangelog.com/) 风格，版本号语义化（SemVer）。

---

## 1. 版本对齐表

> 关键：文档版本、代码版本、prompt 版本需对齐。任何一方变动需在此登记。

| 发布版本 | 文档集版本 | 代码版本 | Prompt 版本 | 发布日期 | 说明 |
|---|---|---|---|---|---|
| v0.1.0-docs | docs-v1 | - | - | 2026-08-24 | 文档先行定稿，11 → 16 份 |
| v0.1.0 | docs-v1 | code-v1 | prompt-v1.0 | 待定 | 首个可用版本（[ROADMAP](./ROADMAP.md) P7 完成） |

### 版本号约定

| 类型 | 格式 | 谁变化 |
|---|---|---|
| 发布版本 | `vMAJOR.MINOR.PATCH` | 整体发布 |
| 文档集版本 | `docs-vN` | 任一文档变更 |
| 代码版本 | `code-vN` | 代码变更 |
| Prompt 版本 | `prompt-vX.Y` | [PROMPT.md](./PROMPT.md) 变更 |

---

## 2. 变更条目

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
