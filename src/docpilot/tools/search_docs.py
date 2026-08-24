"""search_docs 工具：检索本地知识库。

依据：docs/TOOLS.md §1（含返回格式与错误模式）
"""

from __future__ import annotations

from langchain_core.tools import tool

from ..embeddings import get_embeddings
from ..retriever import get_retriever


@tool
def search_docs(query: str) -> str:
    """在本地知识库中检索与问题相关的技术文档片段。

    输入自然语言检索词，返回匹配的文档片段及其来源路径。
    """
    try:
        retriever = get_retriever()
    except Exception:
        return "未在知识库中检索到相关文档。"

    try:
        docs = retriever.invoke(query)
    except Exception:
        return "未在知识库中检索到相关文档。"

    if not docs:
        return "未在知识库中检索到相关文档。"

    # 引用 get_embeddings 触发 settings 加载，确保后续可注入
    _ = get_embeddings

    parts: list[str] = []
    for doc in docs:
        source = doc.metadata.get("source", "?")
        parts.append(f"[来源: {source}]\n{doc.page_content}")
    return "\n---\n".join(parts)
