# 知识库运营 (DATA_CURATION)

> 本地知识库 `docs/` 与日志 `logs/` 的内容规范、更新工作流与质量治理。

RAG 效果的天花板由知识库质量决定。本文与 [EVAL.md](./EVAL.md) D1（检索召回率）直接相关：召回率下降时优先查本文件。

---

## 1. 知识库范围

| 目录 | 内容 | 是否索引 | 是否可被 read_file |
|---|---|---|---|
| `docs/api/` | 接口文档 | ✅（向量化） | ✅ |
| `docs/troubleshooting/` | 排错指南 | ✅ | ✅ |
| `docs/architecture/` | 架构说明 | ✅ | ✅ |
| `docs/<其他>/` | 任意技术文档 | ✅ | ✅ |
| `logs/` | 报错日志 | ❌（按行搜索） | ✅ |

> 注意：`docs/` 内文档会被 [loader.py](./DESIGN.md) 切分并向量化；`logs/` 不会被索引，仅由 `search_logs` 按关键词扫描。

---

## 2. Markdown 文档规范

### 2.1 命名

| 类型 | 命名 | 示例 |
|---|---|---|
| 接口文档 | `<service>-api.md` | `user-service-api.md` |
| 排错指南 | `<现象>-troubleshooting.md` | `oom-troubleshooting.md` |
| 概念说明 | `<topic>.md` | `auth.md` |

- 全小写，连字符分隔
- 不用日期前缀（由版本控制管理）
- 不用中文文件名（兼容性）

### 2.2 结构模板

```markdown
# <标题>

> 一句话摘要

## 背景 / 现象
<问题背景或现象描述>

## 详情 / 步骤
<结构化内容，多用 ## 二级标题>

## 错误码 / 关键信息
<表格或列表，便于 search_logs 联动>

## 参考
<相关文档链接、外部资料>
```

### 2.3 元数据（frontmatter，可选）

```yaml
---
title: 用户服务接口
domain: user
last_review: 2026-08-24
owner: team-backend
---
```

> 当前 loader 不解析 frontmatter，但保留以便后续支持过滤。

### 2.4 切分友好性

[DESIGN.md](./DESIGN.md) §2 切分策略按 `## ` > `### ` > 段落 优先：

| 实践 | 利于召回 |
|---|---|
| 每个二级标题下内容自洽 | ✅ |
| 同一事实分散多处 | ❌ |
| 用表格列错误码 | ✅（search_logs 关键词易命中） |
| 关键术语首次出现给全称+缩写 | ✅ |

---

## 3. 日志规范

### 3.1 文件组织

```
logs/
├── app.log           # 应用主日志
├── <service>.log     # 按服务分文件
└── archive/           # 归档（可选）
```

### 3.2 行格式建议

```
<时间> <级别> <消息>
2026-08-24 10:05:23 ERROR NullPointerException at UserService.create(UserService.java:42)
```

- 时间：`YYYY-MM-DD HH:MM:SS`
- 级别：`INFO` / `WARN` / `ERROR`
- 消息含：异常类名、堆栈位置、错误码

### 3.3 search_logs 友好性

`search_logs` 按关键词正则匹配整行：

| 实践 | 命中率 |
|---|---|
| 错误码独立成词（`40001`） | ✅ |
| 异常类名完整（`NullPointerException`） | ✅ |
| 多个错误信息挤在一行 | ❌（召回噪声大） |
| 用模糊措辞（"出错了"） | ❌ |

---

## 4. 更新工作流

### 4.1 文档新增/修改

```
1. 编辑 docs/<...>.md
2. （可选）用 markdownlint 自检
3. 重新 index：
   docpilot index
4. 验证召回：
   docpilot ask "<相关问题>"
   检查是否命中新内容 + 来源正确
5. 提交（commit message: docs: 新增/更新 <主题>）
```

### 4.2 何时重新 index

| 触发 | 是否需 index |
|---|---|
| 新增 .md | ✅ |
| 修改 .md 内容 | ✅ |
| 删除 .md | ⚠️ 当前实现不删除集合中旧片段，需手动 `rm data/docpilot.db` 重建 |
| 仅改日志 | ❌（logs 不索引） |
| 改配置 | ❌ |

### 4.3 重建索引（彻底）

```bash
# 备份当前
cp data/docpilot.db data/docpilot.db.bak

# 清空重建
rm data/docpilot.db
docpilot index
```

> 注意：`rm data/docpilot.db` 会同时清空文档集合与记忆集合。如需保留记忆，先 `docpilot ask "测试"` 写一条标记，重建后人工恢复（当前版本限制，见 [ROADMAP](./ROADMAP.md) 后续项）。

---

## 5. 质量治理

### 5.1 健康检查清单（定期）

| 检查项 | 频率 | 方法 |
|---|---|---|
| 死链 / 失效引用 | 月 | 人工 grep `docs/` |
| 过期内容（last_review > 6 月） | 季 | frontmatter 字段 |
| 召回率回归 | 月 | [EVAL.md](./EVAL.md) D1 |
| 日志膨胀（单文件 > 50MB） | 月 | `du -sh logs/` |
| 重复内容 | 季 | 人工或向量化聚类 |

### 5.2 召回率下降的归因顺序

当 [EVAL.md](./EVAL.md) D1 召回率下滑：

1. 知识库是否新增了干扰文档（语义混淆）？
2. 是否有内容被删除但未重建索引？
3. 切分是否把关键事实切断？（检查 chunk_size）
4. 嵌入模型是否切换？
5. 文档命名/结构是否违反 §2 规范？

### 5.3 内容所有权

- 每个 `docs/` 子目录建议有 owner（frontmatter `owner` 字段）
- owner 负责定期 review 与过期清理
- 无 owner 的文档进入"待认领"列表

---

## 6. 与其他文档的联动

| 本文档章节 | 联动文档 |
|---|---|
| §2 切分友好 | [DESIGN.md](./DESIGN.md) §2 loader 切分参数 |
| §4 index 工作流 | [API.md](./API.md) §1 index 命令 |
| §5 召回归因 | [EVAL.md](./EVAL.md) D1 |
| §3 日志规范 | [TOOLS.md](./TOOLS.md) §3 search_logs |

---

## 7. 不在本期范围

- 文档版本控制（按文件 mtime 增量索引）→ [ROADMAP](./ROADMAP.md) 后续
- 多格式支持（PDF/DOCX）→ [ROADMAP](./ROADMAP.md) 后续
- 自动摘要/质量打分 → 后续
- 知识图谱化 → 非目标
