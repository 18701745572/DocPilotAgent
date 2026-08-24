"""RAG 检索器。

依据：docs/DESIGN.md §3.1、docs/TOOLS.md §1.4（top_k=4）
"""

from __future__ import annotations

from langchain_milvus import Milvus

from .config import settings
from .embeddings import get_embeddings
from .vectorstore import get_docs_store


def get_retriever(top_k: int | None = None):
    """返回文档集合的检索器。

    依据：docs/TOOLS.md §1.4（top_k 默认 4，余弦相似度）
    """
    store = get_docs_store()
    return store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k or settings.retrieval_top_k},
    )


def retrieve(query: str, top_k: int | None = None) -> list[str]:
    """检索 query 相关文档片段，返回片段文本列表。"""
    retriever = get_retriever(top_k=top_k)
    docs = retriever.invoke(query)
    return [d.page_content for d in docs]
