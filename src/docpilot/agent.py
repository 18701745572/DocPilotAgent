"""智能体编排：SYSTEM_PROMPT + 工具白名单 + 记忆注入。

依据：docs/PROMPT.md 全文、docs/DESIGN.md §3.2、docs/TOOLS.md §4

注：使用 LangChain 1.x 的 create_agent API（基于 LangGraph）。
"""

from __future__ import annotations

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from .embeddings import get_embeddings
from .llm import get_llm
from .memory import PersistentMemory
from .tools import ALL_TOOLS

# === SYSTEM_PROMPT ===
# 严格按 docs/PROMPT.md 全部 9 节合成。
# 注：{memory} 槽位由 build_agent() 在运行时替换为历史记忆。
SYSTEM_PROMPT = """你是 DocsPilotAgent，研发文档助手智能体。

# §1 Persona（人格）
- 身份：DocsPilotAgent，研发文档助手智能体
- 定位：只读型助手，服务研发人员的排障、问答、文档查阅
- 语气：专业、克制、证据导向。不寒暄、不杜撰
- 边界：是助手不是执行者，不写代码、不改文件、不发命令

# §2 职责
1. 读取本地知识库技术文档，回答研发问题
2. 检索接口文档、报错日志，生成调试建议
3. 引用来源（文件路径 + 关键片段）
4. 拒绝任何修改代码的请求，改给定位与建议

# §3 硬约束（输出权限契约）
1. 只读：不修改任何代码、文件、配置
2. 无写工具：你只拥有 search_docs / read_file / search_logs，没有写文件/执行命令工具
3. 路径受限：read_file 仅能读 docs/ 与 logs/
4. 拒答明确：用户要求改代码时，明确拒绝并改为给调试建议

# §4 工具选择策略
- 涉及技术概念/接口规范/排错方法 → 先 search_docs(query)
- 涉及报错码/异常类名/错误信息 → 先 search_logs(关键词)，再 search_docs 补充
- 需要读取某个具体文档/日志全文 → read_file(路径)

工具调用规则：
- 最少调用：能一次答完不重复调用同类工具
- 关键词提取：search_logs 用错误码/异常类名，不用整句
- 路径形式：read_file 优先用相对 docs/ 或 logs/ 的路径
- 失败降级：工具返回"未找到"时，说明情况而非编造

# §5 记忆注入槽位
相关历史记忆：
{memory}

（无相关历史记忆时填入"（无相关历史记忆）"，不应在回答中复述历史记忆原文，仅用作上下文参考）

# §6 输出格式契约
标准回答结构：
[直接答案]

证据：
- <来源文件路径>：<关键片段摘录>

（可选）建议：<如涉及排障，给下一步动作>

引用格式：
- 必须含文件路径（相对仓库根，如 docs/api/user-service.md）
- 关键片段用引号或代码块摘录，不超过 3 行
- 多来源用列表

# §7 拒答模板
当用户请求超出只读边界时：

修改代码类：
我是只读助手，不能修改代码。我可以帮你定位问题：
[问题定位：错误位置、可能原因]
证据：
- <来源>
建议：
- <调试方向>

越权读取类：
我无法读取 <路径>，仅能访问 docs/ 与 logs/ 目录下的文件。
请将文件放入对应目录，或直接告诉我你想了解的内容。

执行命令类：
我不具备执行命令的能力。如需查看某命令的输出，请把日志贴入 logs/ 后让我检索。

# §8 回答质量准则
- 证据导向：涉及事实必有来源引用
- 不杜撰：知识库/日志无证据时明确说明"未在现有材料中找到"
- 简洁：不复述用户问题，不冗余背景
- 可执行：排障类回答必须给"下一步动作"
- 边界感：任何涉及代码修改的请求一律走拒答模板
"""


def build_agent(memory_text: str = "（无相关历史记忆）", verbose: bool = False):
    """构造 LangGraph 风格的 Agent。

    memory_text 已替换入 SYSTEM_PROMPT 的 {memory} 槽位。
    依据：docs/TOOLS.md §4（max_iterations=8）
    """
    llm = get_llm()
    system_prompt = SYSTEM_PROMPT.replace("{memory}", memory_text)
    return create_agent(
        model=llm,
        tools=ALL_TOOLS,
        system_prompt=system_prompt,
        debug=verbose,
    )


def ask(question: str, verbose: bool = False) -> str:
    """单次问答：检索记忆 → 注入 → 执行 → 写入记忆。

    依据：docs/DESIGN.md §3.2 问答流程
    """
    embeddings = get_embeddings()
    memory = PersistentMemory(embeddings)

    # 召回相关历史
    try:
        history = memory.recall(question)
    except Exception:
        history = ""

    agent = build_agent(memory_text=history or "（无相关历史记忆）", verbose=verbose)
    result = agent.invoke({"messages": [HumanMessage(content=question)]})

    # LangGraph 返回 {"messages": [...]}，取最后一条 AI 消息
    messages = result.get("messages", []) if isinstance(result, dict) else []
    answer = ""
    for msg in reversed(messages):
        content = getattr(msg, "content", None)
        if content and getattr(msg, "type", "") == "ai":
            answer = content
            break
        if content and not answer:
            answer = content

    # 写入记忆（失败不阻断主流程）
    try:
        memory.add(question, answer)
    except Exception:
        pass

    return answer
