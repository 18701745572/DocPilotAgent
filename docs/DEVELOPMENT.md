# 开发者指南 (DEVELOPMENT)

> DocPilotAgent 开发环境搭建、本地约定、贡献流程。

面向按 [ROADMAP.md](./ROADMAP.md) 启动 P0 的开发者。本文与 [CONFIG.md](./CONFIG.md) 互补：CONFIG 面向用户配置，本文面向开发者配置。

---

## 1. 前置要求

| 项 | 版本 | 说明 |
|---|---|---|
| Python | ≥ 3.10 | 必须 |
| pip / venv | 系统 Python 自带 | 推荐虚拟环境隔离 |
| Git | 任意 | 版本控制 |
| OpenAI 兼容 API Key | 任意一家 | 见 [CONFIG.md](./CONFIG.md) §3 |

无需 Docker / Milvus 独立服务（用 Milvus Lite 本地文件）。

---

## 2. 环境搭建

```bash
# 1. 克隆
git clone <repo-url> docpilot && cd docpilot

# 2. 虚拟环境
python -m venv .venv && source .venv/bin/activate

# 3. 安装（含开发依赖）
pip install -e ".[dev]"

# 4. 配置
cp .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY

# 5. 验证
docpilot --help
```

---

## 3. 项目结构（开发期）

```
.
├── src/docpilot/         # 源码（pyproject packages.find 指向此）
├── tests/
│   ├── unit/             # 见 TEST_PLAN.md §2
│   ├── integration/     # 见 TEST_PLAN.md §3
│   ├── agent/            # 见 TEST_PLAN.md §4
│   ├── eval/             # 见 EVAL.md §2
│   └── fixtures/         # 固定测试数据（docs/ logs/）
├── docs/                 # 本文档集
├── scripts/              # 开发辅助脚本（lint、index 演示等）
├── pyproject.toml
├── .env.example
└── .gitignore
```

> 运行时产物 `data/` `logs/` 不入版本控制（见 [.gitignore](../.gitignore)）。

---

## 4. 本地开发约定

### 4.1 配置覆盖

开发期可用独立 `.env.dev`：

```bash
set -a && source .env.dev && set +a
```

或直接 export 覆盖单值：

```bash
export VECTOR_DB_PATH=./data/dev.db
export SESSION_ID=dev-alice
```

### 4.2 隔离向量库

不同任务用不同 `VECTOR_DB_PATH`，避免互相污染：

| 场景 | 建议路径 |
|---|---|
| 手动冒烟 | `./data/dev.db` |
| 集成测试 | `tmp_path`（pytest 自动隔离） |
| 评测 | `./data/eval.db` |

### 4.3 测试数据

- 固定测试知识库：`tests/fixtures/docs/`
- 固定测试日志：`tests/fixtures/logs/app.log`
- 不要在生产 `docs/` `logs/` 下放测试样本

---

## 5. 测试

详见 [TEST_PLAN.md](./TEST_PLAN.md)。常用命令：

```bash
# 单元（无需 LLM/向量库，最快）
pytest tests/unit -q

# 集成（需 Milvus Lite，无 LLM）
pytest tests/integration -q

# Agent 行为（需 LLM，默认 mock）
pytest tests/agent -q

# 真实 LLM 跑（成本产生）
DOCPILOT_TEST_LLM=1 pytest tests/agent -q

# 评测集（见 EVAL.md）
python tests/eval/run_retrieval.py
```

### 5.1 LLM Mock 策略

默认 mock，避免单测依赖外部 API 与成本：

| 测试类型 | LLM | 向量库 |
|---|---|---|
| unit | mock | mock |
| integration | mock | 真实（Milvus Lite 临时文件） |
| agent（默认） | mock（固定返回） | 真实 |
| agent（DOCPILOT_TEST_LLM=1） | 真实 | 真实 |

### 5.2 Mock 实现约定

- 用 `unittest.mock` 或 `pytest-mock`
- 固定返回样本放 `tests/fixtures/mock_responses/`
- Mock 的工具调用必须可断言（被调用次数、参数）

---

## 6. 代码规范

### 6.1 风格

- 格式化：`ruff format`
- Lint：`ruff check`
- 类型：`mypy src`（非强制，但新增代码应有类型注解）
- import 排序：`ruff` 默认 `isort` 风格

### 6.2 提交前自检

```bash
ruff format --check src tests
ruff check src tests
pytest tests/unit -q
```

> CI 会跑同样三件套，本地先过可避免来回。

### 6.3 命名

| 对象 | 约定 |
|---|---|
| 模块文件 | snake_case |
| 类 | PascalCase |
| 函数/变量 | snake_case |
| 常量 | UPPER_SNAKE |
| 工具名 | 与 [TOOLS.md](./TOOLS.md) §0 一致 |

---

## 7. IDE 配置建议

### VS Code

`.vscode/settings.json`：

```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "python.analysis.typeCheckingMode": "basic",
  "editor.formatOnSave": true,
  "[python]": {"editor.defaultFormatter": "charliermarsh.ruff"}
}
```

推荐扩展：Python、Ruff、Pylance。

### PyCharm

- 设置 pytest 为默认测试运行器
- 标记 `src` 为 Sources Root
- 标记 `tests` 为 Tests Root

---

## 8. 贡献流程

### 8.1 分支

```
main              受保护，只接 PR
feature/<scope>   新功能
fix/<scope>       修复
docs/<scope>      纯文档
```

### 8.2 提交信息

约定式提交（Conventional Commits）：

```
<type>(<scope>): <subject>

type: feat / fix / docs / test / refactor / chore
scope: agent / tools / memory / cli / docs / config
```

示例：`feat(tools): read_file 增加 symlink 检查`

### 8.3 PR 清单

提 PR 前自检：

- [ ] `ruff format` `ruff check` 通过
- [ ] `pytest tests/unit` 通过
- [ ] 涉及工具/权限改动 → 跑 [TEST_PLAN.md](./TEST_PLAN.md) §4 对抗用例
- [ ] 涉及 prompt → 更新 [PROMPT.md](./PROMPT.md) 版本号
- [ ] 涉及需求 → 更新 [REQUIREMENTS.md](./REQUIREMENTS.md) 与 [TRACEABILITY.md](./TRACEABILITY.md)
- [ ] CHANGELOG 加条目（见 [CHANGELOG.md](./CHANGELOG.md)）

### 8.4 评审重点

| 改动类型 | 必查文档 |
|---|---|
| 工具增减 | [TOOLS.md](./TOOLS.md) + [SECURITY.md](./SECURITY.md) §3 |
| prompt | [PROMPT.md](./PROMPT.md) + [EVAL.md](./EVAL.md) D3 |
| 配置项 | [CONFIG.md](./CONFIG.md) + [API.md](./API.md) §4 |
| 任何权限相关 | [SECURITY.md](./SECURITY.md) 全文 + [TEST_PLAN.md](./TEST_PLAN.md) §4 |

---

## 9. 故障排查（开发期）

| 现象 | 排查 |
|---|---|
| `OPENAI_API_KEY` 报错 | 检查 `.env` 加载；`echo $OPENAI_API_KEY` |
| Milvus 连接失败 | `VECTOR_DB_PATH` 父目录是否存在；`settings.ensure_dirs()` 调用 |
| 索引 0 片段 | `DOCS_DIR` 是否有 `.md`；路径是否相对正确 |
| 记忆召回为空 | 是否先 `add`；`SESSION_ID` 是否一致 |
| 工具未触发 | prompt 是否含工具说明；模型是否支持 tool calling |
| LLM 兼容接口报错 | 模型名是否对；`base_url` 是否带 `/v1` |

---

## 10. 常用脚本（规划）

| 脚本 | 用途 | 产出阶段 |
|---|---|---|
| `scripts/dev_index.sh` | 用 fixtures 索引到 dev.db | P2 |
| `scripts/dev_smoke.sh` | 跑一遍 index/ask/reset | P6 |
| `scripts/eval_all.sh` | 跑全部评测 | P7 |

---

## 11. 不在本指南范围

- 生产部署：本项目为本地 CLI，无部署概念
- 多人协作权限：开源仓库的常规 GitHub 流程
- 持续部署：CI 仅跑测试与 lint，无 CD
