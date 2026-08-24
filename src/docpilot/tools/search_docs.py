"""工具：在知识库中检索相关文档片段（只读）。"""
from __future__ import annotations

from langchain_core.tools import tool

from ..embeddings import get_embeddings
from ..retriever import get_retriever


@tool
def search_docs(query: str) -> str:
    """在本地知识库中检索与问题相关的技术文档片段。

    用于回答研发问题、查阅接口文档或技术规范。
    """
    retriever = get_retriever(get_embeddings())
    docs = retriever.invoke(query)
    if not docs:
        return "未在知识库中检索到相关文档。"
    return "\n---\n".join(
        f"[来源: {d.metadata.get('source', '?')}]\n{d.page_content}" for d in docs
    )
