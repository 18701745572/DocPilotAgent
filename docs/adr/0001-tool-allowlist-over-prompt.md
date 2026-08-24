# ADR-001: 工具白名单优于纯提示词约束

- **状态**：Accepted
- **日期**：2026-08-24
- **决策者**：项目设计
- **关联**：[SECURITY.md](../SECURITY.md) §2、[TOOLS.md](../TOOLS.md) §0、[PROMPT.md](../PROMPT.md) §3

## 背景

项目核心约束之一是"不可修改代码"（[REQUIREMENTS.md](../REQUIREMENTS.md) NFR-1）。LangChain Agent 的工具体系允许任意自定义工具，若仅靠提示词约束"不要改代码"，存在 prompt injection 风险——攻击者可通过精心构造的输入诱导模型"忽略之前指令"调用写工具。

## 决策

采用**工具白名单**机制：`tools/__init__.py` 的 `ALL_TOOLS` 仅包含 `search_docs` / `read_file` / `search_logs` 三个只读工具，根本不提供写文件 / 执行命令 / 网络请求工具。模型从能力层就拿不到修改代码的途径。

## 备选方案

| 方案 | 优点 | 缺点 |
|---|---|---|
| A. 仅提示词约束 | 实现简单 | 可被 prompt injection 绕过 |
| B. 工具白名单（**采纳**） | 物理不可绕过 | 新增工具需走安全评审 |
| C. 输出审查层 | 可拦截输出中的代码 | 无法阻止工具调用本身；增加延迟 |

## 理由

- 提示词约束可被绕过（[SECURITY.md](../SECURITY.md) §3 威胁模型已验证）
- 工具层缺失则模型物理上无法执行写操作，是确定性防御
- 配合提示词层（L1）做双保险，符合最小权限原则

## 影响

- `tools/__init__.py` 的 `ALL_TOOLS` 是唯一工具来源
- 任何新增工具必须满足：只读 + 作用域受限 + 通过 [TEST_PLAN.md](../TEST_PLAN.md) §4 对抗用例
- [SECURITY.md](../SECURITY.md) §5.1 静态审计包含白名单断言

## 后续追踪

- 落地位置：`tools/__init__.py`
- 验证方式：[TEST_PLAN.md](../TEST_PLAN.md) §2.2 白名单单测 + §4 对抗用例
- 复盘触发：考虑新增写工具或执行工具时（应拒绝）
