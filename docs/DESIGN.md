# 架构设计 (DESIGN)

> DocPilotAgent · 技术选型 / 模块划分 / 数据流 / 关键决策

本文与 [REQUIREMENTS.md](./REQUIREMENTS.md) 一一对应，是实现的最高蓝图。

---

## 1. 技术选型（已锁定）

| 维度 | 选型 | 理由 |
|---|---|---|
| 语言 | Python ≥ 3.10 | AI 生态最全 |
| 编排框架 | LangChain ≥ 0.2 | Agent/工具/记忆抽象成熟 |
| LLM | OpenAI 兼容（`langchain-openai` ChatOpenAI） | 通过 base_url 兼容豆包/DeepSeek/Qwen |
| 嵌入 | OpenAI 兼容 Embeddings | 与 LLM 同源，配置一致 |
| 向量库 | **Milvus Lite**（本地文件，无需 Docker） | 练习场景轻量，pymilvus + milvus-lite |
| 文本切分 | `RecursiveCharacterTextSplitter`（Markdown 优先） | 保留语义边界 |
| CLI | Typer + Rich | 类型友好 + 终端美化 |
| 配置 | `python-dotenv` + dataclass | 简单可测 |
| 校验 | Pydantic ≥ 2 | 配置/输出结构化 |

---

## 2. 模块划分

```
src/docpilot/
├── config.py        # 配置加载（环境变量 → Settings dataclass）
├── llm.py           # ChatOpenAI（OpenAI 兼容）封装
├── embeddings.py    # OpenAIEmbeddings 封装
├── vectorstore.py   # Milvus Lite 封装（文档集合 / 记忆集合）
├── loader.py        # Markdown 加载 + 切分
├── retriever.py     # RAG 检索器（文档集合）
├── memory.py        # 跨会话记忆（PersistentMemory，记忆集合）
├── tools/           # 只读工具白名单（核心约束）
│   ├── __init__.py  # ALL_TOOLS 导出（仅只读工具）
│   ├── search_docs.py
│   ├── read_file.py
│   └── search_logs.py
├── agent.py         # 智能体编排（工具白名单 + 记忆注入）
└── cli.py           # CLI 入口（index / ask / reset）
```

---

## 3. 数据流

### 3.1 索引流程（`docpilot index`）

```
docs/**/*.md
   │ (loader.load_and_split)
   ▼
[Document × N]  含 page_content + metadata.source
   │ (vectorstore.get_docs_store + add_documents)
   ▼
Milvus Lite · docs_collection
```

### 3.2 问答流程（`docpilot ask`）

```
用户问题 q
   │
   ├──► memory.recall(q)  ──► 相关历史片段 H
   │
   ├──► AgentExecutor.invoke({input: q, memory: H})
   │        │
   │        ├─ LLM 决策调用只读工具
   │        │   ├─ search_docs → Milvus docs_collection
   │        │   ├─ search_logs → logs/ 关键词扫描
   │        │   └─ read_file   → docs/ logs/ 路径白名单内
   │        │
   │        └─ LLM 生成最终答案 A（含来源引用）
   │
   └──► memory.add(q, A)  ──► Milvus memory_collection（持久化）
```

### 3.3 清空流程（`docpilot reset`）

```
PersistentMemory.reset()
   └─► drop memory_collection（Milvus Lite 本地文件层面）
```

> 注意：当前实现为集合级 drop（清空所有会话）。生产环境应改为按 `session_id` 的 `delete expr`，参见 [ROADMAP.md](./ROADMAP.md)。

---

## 4. 向量库设计

### 4.1 集合划分

| 集合 | 用途 | 元数据 |
|---|---|---|
| `kb_docs`（可配置） | 文档索引 | `source`（文件路径） |
| `kb_memory`（可配置） | 会话记忆 | `session_id`, `type=qa` |

### 4.2 关键参数

- 文件路径：`VECTOR_DB_PATH`（默认 `./data/docpilot.db`）
- `auto_id=True`：自增主键
- `drop_old=False`：index 时不自动重建（避免误删记忆）
- 检索 top_k：文档默认 4，记忆默认 3

### 4.3 嵌入维度

由 `EMBEDDING_MODEL` 决定（如 `text-embedding-3-small` 为 1536 维）。Milvus Lite 自动适配，无需手动声明。

---

## 5. 关键决策记录

### ADR-1 工具白名单优于纯提示词约束
- **背景**：README 要求"不可修改代码"
- **决策**：从工具能力层禁止（不提供写工具），而非仅靠提示词
- **理由**：提示词约束可被绕过（prompt injection）；工具层缺失则模型物理上无法执行
- **影响**：`tools/__init__.py` 的 `ALL_TOOLS` 是唯一工具来源，任何新增工具必须只读

### ADR-2 Milvus Lite 而非 Chroma/FAISS
- **背景**：需要本地持久化向量库
- **决策**：Milvus Lite（用户指定）
- **影响**：依赖 `langchain-milvus` + `pymilvus` + `milvus-lite`；连接参数 `connection_args={"uri": <db_path>}`

### ADR-3 跨会话记忆向量化而非全量保留
- **背景**：长会话上下文超限
- **决策**：每轮 Q&A 向量化存入记忆集合，新问题检索 top-3 注入
- **理由**：避免上下文爆炸，且支持跨会话语义召回
- **权衡**：损失精确时序，换取相关性（如需时序可加时间戳元数据排序）

### ADR-4 路径白名单而非任意文件读取
- **背景**：`read_file` 若开放任意路径会泄露源码/配置
- **决策**：仅允许 `docs/` 与 `logs/` 根下读取，且做 `resolve()` 后的路径校验
- **影响**：见 `tools/read_file.py` 的 `_ALLOWED_ROOTS`

---

## 6. 横切关注点

| 关注点 | 处理 |
|---|---|
| 错误处理 | AgentExecutor `handle_parsing_errors=True`；LLM 解析失败降级 |
| 配置缺失 | `llm.py` / `embeddings.py` 检查 `OPENAI_API_KEY`，缺失时给出明确报错 |
| 目录缺失 | `config.Settings.ensure_dirs()` 自动创建 `data/` 等 |
| 日志脱敏 | 不记录完整问答到磁盘（仅向量化入记忆集合） |

---

## 7. 不在本期范围

- 多用户/多会话并发隔离（仅 `SESSION_ID` 简单隔离）
- 按条件删除单会话记忆（当前为集合级 drop）
- Web UI / REST API
- 流式输出（Stream）
- 增量索引（仅整体重建）
