"""Milvus Lite 向量库封装。

使用本地文件作为 Milvus 存储（无需启动独立服务），
分别承载：
- 文档索引集合（docs_collection）
- 会话记忆集合（memory_collection）
"""
from __future__ import annotations

from langchain_core.embeddings import Embeddings
from langchain_milvus import Milvus

from .config import settings


def get_vectorstore(embeddings: Embeddings, collection_name: str) -> Milvus:
    """返回指向指定集合的 Milvus 向量库实例。

    Parameters
    ----------
    embeddings : Embeddings
        用于写入/查询的嵌入模型。
    collection_name : str
        集合名（文档索引或会话记忆）。
    """
    settings.ensure_dirs()
    return Milvus(
        embedding_function=embeddings,
        connection_args={"uri": str(settings.vector_db_path)},
        collection_name=collection_name,
        auto_id=True,
        drop_old=False,
    )


def get_docs_store(embeddings: Embeddings) -> Milvus:
    """文档索引集合。"""
    return get_vectorstore(embeddings, settings.docs_collection)


def get_memory_store(embeddings: Embeddings) -> Milvus:
    """会话记忆集合。"""
    return get_vectorstore(embeddings, settings.memory_collection)
