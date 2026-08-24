# 配置说明 (CONFIG)

> DocPilotAgent 全部配置项、目录约定与数据源约定

所有配置通过环境变量读取（`.env` 文件，参考 `.env.example`）。

---

## 1. 环境变量

### 1.1 OpenAI 兼容 API

| 变量 | 必填 | 默认 | 说明 |
|---|---|---|---|
| `OPENAI_API_KEY` | ✅ | - | API 密钥 |
| `OPENAI_BASE_URL` | ❌ | `https://api.openai.com/v1` | 兼容接口地址 |
| `LLM_MODEL` | ❌ | `gpt-4o-mini` | Chat 模型名 |
| `EMBEDDING_MODEL` | ❌ | `text-embedding-3-small` | 嵌入模型名 |

### 1.2 数据源目录

| 变量 | 默认 | 说明 |
|---|---|---|
| `DOCS_DIR` | `./docs` | 知识库根目录（递归扫描 `.md`） |
| `LOGS_DIR` | `./logs` | 报错日志目录（关键词搜索） |

### 1.3 向量库（Milvus Lite）

| 变量 | 默认 | 说明 |
|---|---|---|
| `VECTOR_DB_PATH` | `./data/docpilot.db` | Milvus Lite 本地文件 |
| `DOCS_COLLECTION` | `kb_docs` | 文档索引集合名 |
| `MEMORY_COLLECTION` | `kb_memory` | 会话记忆集合名 |

### 1.4 会话

| 变量 | 默认 | 说明 |
|---|---|---|
| `SESSION_ID` | `default` | 会话隔离标识（记忆按此过滤） |

---

## 2. .env 模板

```bash
# OpenAI 兼容
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1
# 切换豆包示例：
# OPENAI_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
# 切换 DeepSeek 示例：
# OPENAI_BASE_URL=https://api.deepseek.com/v1

# 模型
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# 数据源
DOCS_DIR=./docs
LOGS_DIR=./logs

# 向量库
VECTOR_DB_PATH=./data/docpilot.db
DOCS_COLLECTION=kb_docs
MEMORY_COLLECTION=kb_memory

# 会话
SESSION_ID=default
```

---

## 3. 兼容接口对照表

| 提供方 | `OPENAI_BASE_URL` | `LLM_MODEL` 示例 | `EMBEDDING_MODEL` |
|---|---|---|---|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` | `text-embedding-3-small` |
| 豆包（火山方舟） | `https://ark.cn-beijing.volces.com/api/v3` | `doubao-xxx` | `doubao-embedding-xxx` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` | （DeepSeek 暂不提供嵌入，需另配） |
| Qwen | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` | `text-embedding-v3` |

> ⚠️ 当 LLM 与 Embedding 提供方不同时，需扩展为两套 API Key / base_url（见 [ROADMAP.md](./ROADMAP.md) 的"非目标/后续"）。

---

## 4. 目录约定

```
.
├── docs/                 # 知识库（被读取的 .md 文件）
│   ├── api/             # 接口文档
│   └── troubleshooting/ # 排错指南
├── logs/                 # 报错日志（被搜索）
├── data/                 # 运行时生成（gitignore）
│   └── docpilot.db      # Milvus Lite 文件 + 集合
└── .env                  # 本地配置（gitignore）
```

- `docs/` `logs/` 为用户数据，可任意增删
- `data/` 为运行时产物，删除后会丢失索引与记忆（需重新 `index`）

---

## 5. 数据源约定

### 5.1 Markdown 文档

- 编码：UTF-8
- 切分策略：`RecursiveCharacterTextSplitter`，分隔符优先级
  `## ` > `### ` > 段落 > 行 > 空格
- chunk_size=800, overlap=120（可调）
- 元数据：`source`（文件绝对路径）

### 5.2 日志文件

- 编码：UTF-8（忽略非法字符）
- 搜索：正则忽略大小写，按行匹配
- 默认上限：20 条命中

---

## 6. 依赖清单

详见 `pyproject.toml`（实现阶段生成）。核心依赖：

```
langchain >= 0.2
langchain-openai >= 0.1
langchain-community >= 0.2
langchain-milvus >= 0.1
pymilvus >= 2.4
milvus-lite >= 2.4
tiktoken >= 0.7
python-dotenv >= 1.0
typer >= 0.12
rich >= 13
pydantic >= 2
```

Python ≥ 3.10。
