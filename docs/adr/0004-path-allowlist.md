# ADR-004: read_file 采用路径白名单

- **状态**：Accepted
- **日期**：2026-08-24
- **决策者**：项目设计
- **关联**：[SECURITY.md](../SECURITY.md) §2 L3、[TOOLS.md](../TOOLS.md) §2

## 背景

[ADR-001](./0001-tool-allowlist-over-prompt.md) 解决了"不可写"，但 `read_file` 若允许任意路径，仍可泄露源码、配置、密钥、系统文件（`/etc/passwd`、`~/.ssh/id_rsa`）。需要约束读取范围。

## 决策

`read_file` 仅允许读取 `docs/` 与 `logs/` 目录内的文件，且必须：
1. 路径 `resolve()` 规范化（解析 `..` 与符号链接）
2. `relative_to` 校验落在白名单根内
3. 相对路径优先在 `DOCS_DIR` / `LOGS_DIR` 下查找

## 备选方案

| 方案 | 优点 | 缺点 |
|---|---|---|
| A. 任意路径 | 灵活 | 可泄露任意文件 |
| B. 扩展名白名单（仅 .md/.log） | 简单 | 仍可读 `src/*.md` 之类的源码注释 |
| C. 路径白名单（**采纳**） | 精确控制 | 限制稍严 |
| D. 路径 + 扩展名双重白名单 | 最严 | 过度工程 |

## 理由

- 知识库与日志都在固定目录，无需读其他位置
- 路径白名单 + resolve 校验可同时防御：
  - 直接绝对路径越权（`/etc/passwd`）
  - 相对路径穿越（`../../src/main.py`）
  - 符号链接逃逸（`docs/link.md` → `/etc/passwd`，resolve 后越界被拒）

## 影响

- `tools/read_file.py` 维护 `_ALLOWED_ROOTS = [docs_dir, logs_dir]`
- [TOOLS.md](../TOOLS.md) §2.4 描述校验逻辑
- [SECURITY.md](../SECURITY.md) §4 UC-S2/S3/S6 为对抗用例
- [TEST_PLAN.md](../TEST_PLAN.md) §2.3 覆盖穿越测试

## 后续追踪

- 落地位置：`tools/read_file.py`
- 验证方式：[TEST_PLAN.md](../TEST_PLAN.md) §2.3 + §4 UC-S2/S3/S6
- 复盘触发：需读取 docs/logs 之外文件时（应通过迁移文件而非放开白名单）
- 已知缺口：符号链接场景需在实现阶段验证 `resolve()` 行为（见 [SECURITY.md](../SECURITY.md) §6）
