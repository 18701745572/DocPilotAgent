# DocPilotAgent

研发文档助手智能体（只读型 RAG 助手）。

读取本地知识库技术文档，回答研发人员问题；可检索接口文档、报错日志，生成调试建议。**不可修改代码**。

## 特性

- **RAG + 多数据源**：本地 Markdown 知识库 + 报错日志检索
- **跨会话记忆**：问答历史向量化持久化到 Milvus Lite，按语义相关性召回
- **输出权限约束**：只读工具白名单，从能力层杜绝代码修改（工具层 + 提示词双保险）
- **OpenAI 兼容**：可切换 OpenAI / 豆包 / DeepSeek / Qwen 等接口
- **CLI 工具**：`index` / `ask` / `reset`

## 安装

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env   # 编辑填入 API Key
```

## 配置

编辑 `.env`：

| 变量 | 说明 |
|---|---|
| `OPENAI_API_KEY` | API 密钥 |
| `OPENAI_BASE_URL` | 兼容接口地址（可换豆包/DeepSeek） |
| `LLM_MODEL` / `EMBEDDING_MODEL` | 模型名 |
| `DOCS_DIR` / `LOGS_DIR` | 知识库 / 日志目录 |
| `VECTOR_DB_PATH` | Milvus Lite 本地文件 |

## 用法

```bash
# 1. 索引知识库
docpilot index

# 2. 提问
docpilot ask "如何排查 OOM？"

# 3. 显示中间步骤
docpilot ask "用户接口 40001 是什么错误？" --verbose

# 4. 清空跨会话记忆
docpilot reset
```

## 架构

```
CLI (cli.py)
 └─ agent.py ── 工具白名单 (tools/, 全部只读)
                ├─ search_docs → Milvus 文档集合
                ├─ read_file   → docs/ logs/ (路径白名单)
                └─ search_logs → logs/
 └─ memory.py  → Milvus 记忆集合 (跨会话持久化)
```

## 练习点

- RAG + 多数据源接入
- 记忆管理（跨会话向量化持久化）
- 输出权限约束（工具白名单 + 提示词）

## License

Apache-2.0
