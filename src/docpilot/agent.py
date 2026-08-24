"""智能体编排：工具白名单 + 跨会话记忆注入。

练习点串联：
- 工具白名单（tools.ALL_TOOLS）确保只读；
- 跨会话记忆（PersistentMemory）按语义相关性召回历史片段注入 prompt；
- system prompt 再次强调输出权限约束（双保险）。
"""
from __future__ import annotations

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .embeddings import get_embeddings
from .llm import get_llm
from .memory import PersistentMemory
from .tools import ALL_TOOLS

SYSTEM_PROMPT = """你是 DocPilotAgent，一个研发文档助手智能体。

职责：
- 读取本地知识库技术文档，回答研发人员问题；
- 可检索接口文档、报错日志，生成调试建议。

硬约束（输出权限约束）：
- 你是只读助手，绝不能修改任何代码、文件或配置；
- 你不拥有任何写文件 / 执行命令的工具，只能查询与读取；
- 当用户要求修改代码时，明确说明职责限制，改为给出调试建议或定位说明。

工作方式：
- 优先用 search_docs 检索知识库；
- 需查阅日志用 search_logs；
- 需读取具体文件用 read_file（仅限 docs / logs 目录）；
- 回答需引用文档来源。

相关历史记忆：
{memory}
"""


def build_agent(verbose: bool = False) -> AgentExecutor:
    """构造带工具白名单的智能体执行器。"""
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, ALL_TOOLS, prompt)
    return AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        verbose=verbose,
        handle_parsing_errors=True,
        max_iterations=8,
    )


def ask(question: str, verbose: bool = False) -> str:
    """便捷入口：注入相关历史记忆 → 提问 → 持久化本轮问答。"""
    embeddings = get_embeddings()
    memory = PersistentMemory(embeddings)
    history = memory.recall(question)

    executor = build_agent(verbose=verbose)
    result = executor.invoke(
        {"input": question, "memory": history or "（无相关历史记忆）"}
    )
    answer = result.get("output", "")
    # 持久化本轮问答，供后续跨会话检索
    memory.add(question, answer)
    return answer
