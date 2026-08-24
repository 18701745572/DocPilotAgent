# 开发路线图 (ROADMAP)

> DocPilotAgent · 以终为始：文档先行，实现按阶段推进

本文档定义从骨架到可用的阶段划分与验收标准。每个阶段完成即满足 [REQUIREMENTS.md](./REQUIREMENTS.md) 对应条目。

---

## 阶段总览

| 阶段 | 主题 | 产出 | 对应需求 |
|---|---|---|---|
| P0 | 项目骨架 | pyproject / 配置加载 / 目录结构 | NFR-5,6 |
| P1 | 基础设施 | LLM + Embeddings + Milvus 封装 | NFR-3,4 |
| P2 | RAG 链路 | loader + retriever + 文档索引 | FR-1,3.1 |
| P3 | 跨会话记忆 | PersistentMemory | FR-4 |
| P4 | 只读工具白名单 | tools/（核心约束） | NFR-1,2, 第 4 节 |
| P5 | 智能体编排 | agent.py | FR-2 |
| P6 | CLI | index/ask/reset | FR-5 |
| P7 | 验收 | 端到端冒烟 + 文档对齐 | 全部 |

---

## P0 · 项目骨架

- [ ] `pyproject.toml`：依赖、入口 `docpilot = docpilot.cli:main`
- [ ] `.env.example` / `.gitignore`
- [ ] `src/docpilot/__init__.py`
- [ ] `config.py`：`Settings` dataclass + `ensure_dirs()`

**验收**：`python -m compileall src` 通过；`Settings` 能读取示例 `.env`。

---

## P1 · 基础设施

- [ ] `llm.py`：`get_llm()` 返回 ChatOpenAI
- [ ] `embeddings.py`：`get_embeddings()` 返回 OpenAIEmbeddings
- [ ] `vectorstore.py`：`get_docs_store` / `get_memory_store` 封装 Milvus Lite

**验收**：
- 缺 `OPENAI_API_KEY` 时报错信息明确
- 能连接 Milvus Lite 文件并创建集合

---

## P2 · RAG 链路

- [ ] `loader.py`：`load_and_split()` 递归读取 + 切分
- [ ] `retriever.py`：`get_retriever()` + `retrieve()`
- [ ] 切分参数 `chunk_size=800 / overlap=120`，分隔符按 Markdown 结构

**验收**：
- 示例 `docs/` 下 2 篇 .md 能切分为 ≥2 片段
- 检索 "OOM" 能命中 `troubleshooting/oom.md` 片段

---

## P3 · 跨会话记忆

- [ ] `memory.py`：`PersistentMemory`
  - `add(q, a)` 向量化存入记忆集合
  - `recall(query, k=3)` 按语义召回
  - `reset()` drop 集合
- [ ] `session_id` 过滤

**验收**：
- 写入后重启进程，`recall` 仍能召回
- `reset` 后 `recall` 返回空串

---

## P4 · 只读工具白名单（核心练习点）

- [ ] `tools/search_docs.py`：检索文档集合
- [ ] `tools/read_file.py`：读取 docs/logs 白名单内文件
- [ ] `tools/search_logs.py`：关键词搜索 logs/
- [ ] `tools/__init__.py`：`ALL_TOOLS` 仅含上述 3 个只读工具

**验收**：
- `ALL_TOOLS` 不含任何写/执行工具
- `read_file` 拒绝访问 `docs/logs` 之外的路径
- 模型无法调用任何修改代码的工具（验证工具列表）

---

## P5 · 智能体编排

- [ ] `agent.py`：
  - SYSTEM_PROMPT 含约束声明（双保险）
  - `build_agent()` 用 `create_tool_calling_agent`
  - `ask()` 注入 `memory.recall` 结果 → 执行 → `memory.add`

**验收**：
- 提问能触发工具调用
- 回答包含来源引用
- "帮我改代码"类请求被拒绝并改为调试建议

---

## P6 · CLI

- [ ] `cli.py`：
  - `index` 命令
  - `ask QUESTION [--verbose]` 命令
  - `reset` 命令
  - Rich Panel 输出

**验收**：
- `docpilot --help` 列出三命令
- `docpilot index` 提示写入片段数
- `docpilot ask` 输出 Panel

---

## P7 · 验收

- [ ] 端到端冒烟（参考 REQUIREMENTS 第 7 节验收清单）
- [ ] 至少切换一种兼容接口（豆包/DeepSeek）验证
- [ ] README 与实际命令一致
- [ ] 示例 `docs/` + `logs/` 可复现 UC-1~UC-4

---

## 后续 / 非目标（不在本期）

按重要性排序，仅供演进参考：

1. **按会话删除记忆**：当前 `reset` 为集合级 drop，应改为 `delete expr=session_id`
2. **LLM / Embedding 分离配置**：当前共用一套 Key/base_url，应支持两套
3. **增量索引**：当前整体重建，应按文件 mtime 增量
4. **流式输出**：`ask` 支持 `--stream`
5. **交互式 REPL**：`docpilot chat` 多轮对话
6. **记忆时序**：记忆元数据加时间戳，召回时按相关性+时间排序
7. **Web UI / REST API**：从 CLI 扩展为服务
8. **多格式支持**：除 .md 外支持 .pdf / .docx

---

## 验收检查表（最终）

实现完成后逐项勾选，对应 [REQUIREMENTS.md](./REQUIREMENTS.md) 第 7 节：

- [ ] `docpilot index` 索引并提示片段数
- [ ] `docpilot ask` 回答含来源
- [ ] 跨进程重启后记忆可召回
- [ ] `docpilot reset` 后记忆清空
- [ ] 工具列表无写工具
- [ ] `read_file` 拒绝白名单外路径
- [ ] 至少一种兼容接口验证通过
