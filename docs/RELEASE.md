# 发布门禁 (RELEASE)

> DocPilotAgent 发版前的检查、版本策略与回滚流程。

发版是 [ROADMAP.md](./ROADMAP.md) P7 之后的最后一道闸。任何发布必须通过本文检查表。

---

## 1. 发布类型

| 类型 | 触发 | 闸门 |
|---|---|---|
| Major | 不兼容变更（约束松动、命令删除） | §3 全表 + 评审会议 |
| Minor | 新功能/新文档（向后兼容） | §3 全表 |
| Patch | 修复 | §3 必查项（标 ✅） |
| Hotfix | 紧急修复 | §3 必查项 + 事后补全 |

---

## 2. 版本号

遵循 [CHANGELOG.md](./CHANGELOG.md) §5 SemVer 策略。

```
vMAJOR.MINOR.PATCH
```

- 1.0.0 前：`v0.x.y` 预发布，无严格兼容承诺
- 1.0.0 起：严格 SemVer

---

## 3. 发版检查表

### 3.1 必查项（任何发布）

- [ ] `ruff format --check src tests` 通过
- [ ] `ruff check src tests` 无错误
- [ ] `pytest tests/unit -q` 全绿
- [ ] `pytest tests/integration -q` 全绿
- [ ] [CHANGELOG.md](./CHANGELOG.md) 已加 `[Unreleased]` 条目并移入新版本段
- [ ] [README.md](../README.md) 与实际命令一致
- [ ] 版本号已在 `pyproject.toml` / `__init__.py` 更新

### 3.2 全表（Minor / Major）

#### 代码层
- [ ] `pytest tests/agent -q` 全绿（含对抗用例 T-S1~S6）
- [ ] 至少一种兼容接口验证通过（豆包/DeepSeek/Qwen 选一）
- [ ] 端到端冒烟（[TEST_PLAN.md](./TEST_PLAN.md) §5）通过
- [ ] 无未关闭的 P0/P1 issue

#### 评估层（[EVAL.md](./EVAL.md)）
- [ ] D1 检索召回率 ≥ 80%
- [ ] D2 答案正确性平均 ≥ 4.0
- [ ] D3 约束遵守率 = 100%
- [ ] D4 引用完整率 ≥ 90%
- [ ] 与上次基准对比无 > 5% 退化
- [ ] 成本/延迟满足 [EVAL.md](./EVAL.md) §5 目标

#### 文档层
- [ ] [TRACEABILITY.md](./TRACEABILITY.md) 已更新需求→实现映射
- [ ] 涉及工具改动 → [TOOLS.md](./TOOLS.md) + [SECURITY.md](./SECURITY.md) §3 同步
- [ ] 涉及 prompt → [PROMPT.md](./PROMPT.md) §9 版本号递增
- [ ] 涉及配置 → [CONFIG.md](./CONFIG.md) + [API.md](./API.md) §4 同步
- [ ] [ADR](./adr/) 有新决策时已归档

#### 安全层
- [ ] [SECURITY.md](./SECURITY.md) §4 全部对抗用例通过
- [ ] `ALL_TOOLS` 白名单断言通过（无写/执行工具）
- [ ] `read_file` 路径穿越对抗通过

---

## 4. 发布流程

```
1. 冻结代码（main 分支保护）
2. 跑 §3 检查表，全部通过
3. 更新版本号 + CHANGELOG
4. 打 tag：git tag vMAJOR.MINOR.PATCH
5. 推 tag：git push origin vMAJOR.MINOR.PATCH
6. 构建：python -m build
7. （可选）发布到 PyPI
8. 在 GitHub Release 附 CHANGELOG 条目
9. 解冻 main
```

---

## 5. 回滚策略

### 5.1 代码回滚

```bash
# 回到上一版本 tag
git checkout v<previous-version>
pip install -e .
```

### 5.2 数据回滚

| 数据 | 回滚方式 |
|---|---|
| 向量库 `data/docpilot.db` | 用 `data/docpilot.db.bak` 恢复（发布前应备份） |
| 知识库 `docs/` | git checkout 恢复 |
| 日志 `logs/` | git checkout 恢复 |
| 记忆集合 | **不可回滚**（已 drop 即丢失，[ROADMAP](./ROADMAP.md) 后续补按会话删除） |

### 5.3 回滚决策

| 情况 | 动作 |
|---|---|
| 安全约束被绕过 | 立即回滚 + 热 fix + [SECURITY.md](./SECURITY.md) 加对抗用例 |
| 召回率退化 > 10% | 回滚或 hotfix |
| 普通 bug | 下一 patch 修，不回滚 |

---

## 6. 发布候选（RC）

Major / Minor 发布前可发 RC：

```
v1.0.0-rc1
v1.0.0-rc2
...
```

RC 需跑 §3 全表，但允许存在已知非阻塞问题（在 Release notes 声明）。

---

## 7. 发布物清单

每次发布产出：

| 物 | 说明 |
|---|---|
| Git tag | `vMAJOR.MINOR.PATCH` |
| 源码包 | `dist/docpilot-*.tar.gz` |
| wheel | `dist/docpilot-*.whl` |
| Release notes | 引用 [CHANGELOG.md](./CHANGELOG.md) 对应段 |
| 文档快照 | 可选，归档 docs/ 至 release 分支 |

---

## 8. 与其他文档的联动

| 本文章节 | 联动 |
|---|---|
| §3 评估门禁 | [EVAL.md](./EVAL.md) |
| §3 安全门禁 | [SECURITY.md](./SECURITY.md) + [TEST_PLAN.md](./TEST_PLAN.md) §4 |
| §3 文档门禁 | [TRACEABILITY.md](./TRACEABILITY.md) |
| §4 发布流程 | [CHANGELOG.md](./CHANGELOG.md) |
| §5 回滚 | [DATA_CURATION.md](./DATA_CURATION.md) §4.3 |
