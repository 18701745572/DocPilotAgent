# CLI 接口规范 (API)

> DocPilotAgent 命令行接口

入口命令：`docpilot`（由 `pyproject.toml` 的 `[project.scripts]` 注册）。

---

## 命令总览

```
docpilot [OPTIONS] COMMAND [ARGS]...

COMMANDS:
  index   索引本地知识库到 Milvus Lite
  ask     向智能体提问
  reset   清空跨会话记忆
  --help  显示帮助
```

---

## 1. `docpilot index`

索引 `DOCS_DIR` 下所有 Markdown 到 Milvus Lite 文档集合。

### 行为
1. 递归扫描 `DOCS_DIR` 下的 `*.md`
2. 按 Markdown 结构切分（chunk_size=800, overlap=120）
3. 向量化后写入 `DOCS_COLLECTION` 集合
4. 输出写入片段数

### 输出（示例）

```
加载知识库：./docs
切分为 12 个片段，写入 Milvus Lite...
索引完成，共写入 12 个片段。
```

### 退出码
- `0` 成功
- `1` 未找到任何 Markdown（提示用户放入文档）

### 边界
- 空目录：报错退出 1
- 已有索引：追加写入（如需覆盖，先手动删除 `VECTOR_DB_PATH`）

---

## 2. `docpilot ask`

单次提问。

### 用法

```
docpilot ask QUESTION [--verbose]
```

### 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `QUESTION` | string | 是 | 要提问的问题 |
| `--verbose` / `-v` | flag | 否 | 显示中间步骤（工具调用、检索结果） |

### 行为
1. 从记忆集合检索与问题相关的历史片段
2. 注入 SYSTEM_PROMPT（含约束 + 历史）
3. AgentExecutor 调用只读工具 + LLM 生成答案
4. 将本轮 Q&A 向量化存入记忆集合
5. 输出答案（Rich Panel 渲染）

### 输出（示例）

```
┌─ 问题 ────────────────────────────┐
│ 用户接口 40001 是什么错误？        │
└───────────────────────────────────┘
┌─ 回答 ────────────────────────────┐
│ 错误码 40001 表示"用户名已存在"... │
│ 来源：docs/api/user-service.md     │
└───────────────────────────────────┘
```

### 退出码
- `0` 成功
- 非 0：API Key 缺失 / 网络错误 / AgentExecutor 异常

---

## 3. `docpilot reset`

清空跨会话记忆。

### 行为
- drop `MEMORY_COLLECTION` 集合（Milvus Lite 文件层面）

### 输出

```
已清空跨会话记忆。
```

### 退出码
- `0` 成功（含集合本不存在的情形）

### 注意
- 当前为集合级 drop，会清除**所有会话**的记忆
- 文档索引不受影响

---

## 4. 全局选项

以下选项对子命令也生效（通过环境变量）：

| 选项 | 环境变量 | 默认 | 说明 |
|---|---|---|---|
| API 密钥 | `OPENAI_API_KEY` | - | 必填 |
| 接口地址 | `OPENAI_BASE_URL` | `https://api.openai.com/v1` | 兼容豆包/DeepSeek |
| LLM 模型 | `LLM_MODEL` | `gpt-4o-mini` | - |
| 嵌入模型 | `EMBEDDING_MODEL` | `text-embedding-3-small` | - |
| 知识库目录 | `DOCS_DIR` | `./docs` | - |
| 日志目录 | `LOGS_DIR` | `./logs` | - |
| 向量库路径 | `VECTOR_DB_PATH` | `./data/docpilot.db` | Milvus Lite 文件 |
| 会话 ID | `SESSION_ID` | `default` | 记忆隔离用 |

完整说明见 [CONFIG.md](./CONFIG.md)。

---

## 5. 退出码汇总

| 码 | 含义 |
|---|---|
| 0 | 成功 |
| 1 | 输入/配置类错误（空目录、缺 API Key 等） |
| 2 | 调用 LLM 失败 |
| 3 | 向量库操作失败 |
