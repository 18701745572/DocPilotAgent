# DocPilotAgent

> 研发文档助手智能体 · 只读型 RAG 助手

读取本地知识库技术文档，回答研发人员问题；可检索接口文档、报错日志，生成调试建议。**不可修改代码**。

---

## 设计目标（三大练习点）

| 练习点 | 落地方式 |
|---|---|
| **RAG + 多数据源** | 本地 Markdown 知识库 + 报错日志检索 |
| **记忆管理** | 跨会话问答历史向量化持久化到 Milvus Lite，按语义相关性召回 |
| **输出权限约束** | 只读工具白名单（工具层 + 提示词 + 路径白名单三层防御），从能力层杜绝代码修改 |

---

## 文档索引（以终为始 · 17 份）

本项目采用「文档先行」方式（[ADR-005](docs/adr/0005-docs-first.md)），需求、设计、接口、安全、评估、测试、运营已全部锁定为最终形态。

> **新入手者直接看 [docs/EXECUTION_GUIDE.md](docs/EXECUTION_GUIDE.md)** —— 按 P0~P7 共 30 条提示词顺序执行即可从零完成项目。

### 规格层（做什么）
| 文档 | 内容 |
|---|---|
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | 功能/非功能需求、输出权限约束、典型用例、验收标准 |

### 设计层（怎么做）
| 文档 | 内容 |
|---|---|
| [docs/DESIGN.md](docs/DESIGN.md) | 技术选型、模块划分、数据流、向量库设计 |
| [docs/PROMPT.md](docs/PROMPT.md) | 智能体 persona、工具选择策略、拒答模板、引用格式、记忆槽位 |
| [docs/TOOLS.md](docs/TOOLS.md) | 工具白名单规格（schema、返回格式、错误模式、示例 I/O） |
| [docs/SECURITY.md](docs/SECURITY.md) | 三层防御模型、威胁模型、对抗用例、权限审计 |
| [docs/adr/](docs/adr/README.md) | 架构决策记录（ADR-001~005 + 模板） |

### 接口层（怎么用）
| 文档 | 内容 |
|---|---|
| [docs/API.md](docs/API.md) | CLI 命令规范（index/ask/reset）、参数、退出码 |
| [docs/CONFIG.md](docs/CONFIG.md) | 环境变量、`.env` 模板、兼容接口对照、目录约定 |

### 验证层（怎么验）
| 文档 | 内容 |
|---|---|
| [docs/EVAL.md](docs/EVAL.md) | 4 维评估（检索召回/答案正确/约束遵守/引用完整）、评测集、回归基准 |
| [docs/TEST_PLAN.md](docs/TEST_PLAN.md) | 测试金字塔、单元/集成/Agent 对抗/E2E 用例、CI 集成 |

### 管理层（怎么推进）
| 文档 | 内容 |
|---|---|
| [docs/ROADMAP.md](docs/ROADMAP.md) | P0~P7 阶段划分、任务拆分、阶段验收标准 |
| [docs/TRACEABILITY.md](docs/TRACEABILITY.md) | 需求→模块→命令→阶段→测试→评测双向追溯矩阵 |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | 文档/代码/prompt 版本对齐与变更登记 |
| [docs/RELEASE.md](docs/RELEASE.md) | 发版门禁、版本策略、回滚流程 |

### 工程运营层（怎么养护）
| 文档 | 内容 |
|---|---|
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | 开发环境、测试、mock、IDE、贡献流程 |
| [docs/DATA_CURATION.md](docs/DATA_CURATION.md) | 知识库/日志内容规范、index 工作流、质量治理 |

### 执行层（怎么从头做）
| 文档 | 内容 |
|---|---|
| [docs/EXECUTION_GUIDE.md](docs/EXECUTION_GUIDE.md) | P0~P7 共 30 条可顺序执行的提示词,任何人按序执行即可完成项目 |

---

## 技术选型（已锁定）

- **语言**：Python ≥ 3.10
- **编排**：LangChain ≥ 0.2
- **LLM**：OpenAI 兼容（可切豆包/DeepSeek/Qwen）
- **向量库**：Milvus Lite（本地文件，无需 Docker）
- **CLI**：Typer + Rich

详见 [docs/DESIGN.md](docs/DESIGN.md) 第 1 节。

---

## 快速开始（实现完成后）

```bash
pip install -e .
cp .env.example .env   # 填入 OPENAI_API_KEY
docpilot index          # 索引 docs/
docpilot ask "如何排查 OOM？"
docpilot reset          # 清空跨会话记忆
```

> 当前仓库仅含文档，代码尚未实现。开发计划见 [docs/ROADMAP.md](docs/ROADMAP.md)。

---

## 架构概览

```
CLI
 └─ Agent ── 只读工具白名单（无写工具）
              ├─ search_docs → Milvus 文档集合
              ├─ read_file   → docs/logs 路径白名单
              └─ search_logs → logs/ 关键词搜索
 └─ Memory  → Milvus 记忆集合（跨会话持久化）
```

完整数据流与模块职责见 [docs/DESIGN.md](docs/DESIGN.md)，权限模型见 [docs/SECURITY.md](docs/SECURITY.md)。

---

## License

Apache-2.0
