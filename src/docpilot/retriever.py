"""RAG 检索器：基于 Milvus 文档集合做相似度检索。"""
from __future__ import annotations

from langchain_core.embeddings import Embeddings

from .config import settings
from .vectorstore import get_docs_store


def get_retriever(embeddings: Embeddings, top_k: int | None = None):
    """返回文档集合的相似度检索器。"""
    store = get_docs_store(embeddings)
    return store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k or settings.retrieval_top_k},
    )


def retrieve(query: str, embeddings: Embeddings, top_k: int | None = None) -> list[str]:
    """便捷函数：检索并返回命中文档的文本片段。"""
    retriever = get_retriever(embeddings, top_k)
    docs = retriever.invoke(query)
    return [d.page_content for d in docs]
