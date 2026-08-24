"""Milvus Lite 封装：文档集合 / 记忆集合。

依据：docs/DESIGN.md §4（向量库设计）、ADR-0002-milvus-lite.md
"""

from __future__ import annotations

from langchain_milvus import Milvus

from .config import settings
from .embeddings import get_embeddings


def _get_vectorstore(collection_name: str) -> Milvus:
    """私有：用指定集合名创建 Milvus 实例。

    依据：docs/DESIGN.md §4.2 关键参数
    """
    settings.ensure_dirs()
    return Milvus(
        embedding_function=get_embeddings(),
        connection_args={"uri": str(settings.vector_db_path)},
        collection_name=collection_name,
        auto_id=True,
        drop_old=False,
    )


def get_docs_store() -> Milvus:
    """文档索引集合。"""
    return _get_vectorstore(settings.docs_collection)


def get_memory_store() -> Milvus:
    """会话记忆集合。"""
    return _get_vectorstore(settings.memory_collection)
