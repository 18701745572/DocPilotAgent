# 工具规范 (TOOLS)

> DocPilotAgent 智能体可用工具的完整规格。

本文与 [PROMPT.md](./PROMPT.md) 第 4 节、[SECURITY.md](./SECURITY.md) 第 2 节配套。**工具白名单仅含本文列出的 3 个只读工具**。

---

## 0. 工具白名单总览

| 工具 | 类型 | 作用域 | 写权限 |
|---|---|---|---|
| `search_docs` | 只读检索 | Milvus 文档集合 | ❌ |
| `read_file` | 只读文件 | `docs/` `logs/` 路径白名单 | ❌ |
| `search_logs` | 只读检索 | `logs/` 目录 | ❌ |

**核心约束**：本白名单不包含任何写文件 / 执行命令 / 网络请求工具。新增工具必须满足：
1. 只读
2. 作用域受限
3. 经 [SECURITY.md](./SECURITY.md) 对抗用例验证

---

## 1. `search_docs`

### 1.1 用途
在本地知识库（Milvus 文档集合）中检索与问题相关的技术文档片段。

### 1.2 入参 schema

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `query` | string | 是 | 自然语言检索词 |

### 1.3 返回格式

```
[来源: <文件路径>]
<文档片段内容>
---
[来源: <文件路径>]
<文档片段内容>
```

无命中时返回：`未在知识库中检索到相关文档。`

### 1.4 行为细节
- top_k：4（由 `settings.retrieval_top_k` 控制）
- 相似度算法：余弦相似度（Milvus 默认）
- 元数据透传：`source` 字段

### 1.5 错误模式

| 情况 | 返回 |
|---|---|
| 集合为空（未 index） | `未在知识库中检索到相关文档。` |
| 嵌入服务不可用 | 抛异常，由 AgentExecutor 捕获并降级 |

### 1.6 示例

**输入**：`query = "如何排查 OOM"`

**输出**：
```
[来源: docs/troubleshooting/oom.md]
## 现象
服务进程被 OOM Killer 终止...
---
[来源: docs/troubleshooting/oom.md]
## 排查步骤
1. dmesg \| grep -i oom 确认被杀进程...
```

---

## 2. `read_file`

### 2.1 用途
读取本地文件内容。**仅允许 `docs/` 与 `logs/` 目录内的文件**。

### 2.2 入参 schema

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file_path` | string | 是 | 相对 `docs/` 或 `logs/` 的路径，或这些目录内的绝对路径 |

### 2.3 返回格式
- 成功：文件文本内容（UTF-8）
- 失败：人类可读的错误串（见 2.5）

### 2.4 路径白名单逻辑

```
1. 若 file_path 为相对路径：
   - 先尝试 (DOCS_DIR / file_path)
   - 再尝试 (LOGS_DIR / file_path)
   - 命中且 resolve() 后仍在白名单根内 → 读取
2. 若为绝对路径：
   - resolve() 后必须落在 DOCS_DIR 或 LOGS_DIR 内
3. 否则：拒绝
```

> 关键：用 `Path.resolve()` 规范化后再做 `relative_to` 校验，**防御符号链接与 `..` 穿越**。

### 2.5 错误模式

| 情况 | 返回 |
|---|---|
| 路径不在白名单 | `拒绝访问：<path> 不在允许的目录（docs/logs）内。` |
| 文件不存在 | `文件不存在：<path>` |
| 相对路径在两目录都未命中 | `未找到文件：<path>` |

### 2.6 示例

**输入**：`file_path = "api/user-service.md"`

**输出**：`# 用户服务接口文档 ...`

**越权输入**：`file_path = "/etc/passwd"`

**输出**：`拒绝访问：/etc/passwd 不在允许的目录（docs/logs）内。`

---

## 3. `search_logs`

### 3.1 用途
在 `logs/` 目录中按关键词搜索报错日志行。

### 3.2 入参 schema

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `keyword` | string | 是 | - | 搜索关键词（错误码/异常类名/报错片段） |
| `max_results` | int | 否 | 20 | 最大命中行数 |

### 3.3 返回格式

```
<文件路径>:<行号>: <日志行>
<文件路径>:<行号>: <日志行>
...（已达到上限 N 条）
```

无命中：`未在日志中找到关键词：<keyword>`

### 3.4 行为细节
- 大小写不敏感（`re.IGNORECASE`）
- 递归扫描 `logs/` 下所有文件
- 编码：UTF-8（忽略非法字符）

### 3.5 错误模式

| 情况 | 返回 |
|---|---|
| `logs/` 不存在 | `日志目录不存在：<path>` |
| 读取某文件失败 | 跳过该文件继续扫描 |

### 3.6 示例

**输入**：`keyword = "NullPointerException"`

**输出**：
```
logs/app.log:2: 2026-08-24 10:05:23 ERROR NullPointerException at UserService.create(UserService.java:42)
```

---

## 4. 工具调用约束（Agent 层）

| 约束 | 实现位置 |
|---|---|
| 最大迭代次数 | `AgentExecutor.max_iterations=8` |
| 解析失败降级 | `handle_parsing_errors=True` |
| 工具白名单绑定 | `tools/__init__.py` 的 `ALL_TOOLS` |

---

## 5. 工具演进规则

- **新增工具**：必须只读 + 作用域受限 + 通过 [TEST_PLAN.md](./TEST_PLAN.md) 对抗测试
- **删除工具**：更新 `ALL_TOOLS` 与本文件
- **参数变更**：同步 [API.md](./API.md) 与 [EVAL.md](./EVAL.md) 评测用例
