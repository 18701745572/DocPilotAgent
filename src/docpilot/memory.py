"""跨会话记忆：向量化持久化到 Milvus 记忆集合。

依据：docs/DESIGN.md §3.2/3.3、ADR-0003-vectorized-memory.md、docs/PROMPT.md §5
"""

from __future__ import annotations

from langchain_openai import OpenAIEmbeddings

from .config import settings
from .vectorstore import get_memory_store


class PersistentMemory:
    """跨会话记忆。

    每轮 Q&A 向量化存入记忆集合；新问题按语义召回 top-3 注入 prompt。
    跨进程持久化（写入 Milvus Lite 本地文件即不丢失）。
    """

    def __init__(self, embeddings: OpenAIEmbeddings | None = None, session_id: str | None = None) -> None:
        self.embeddings = embeddings or _lazy_embeddings()
        self.session_id = session_id or settings.session_id
        self.store = get_memory_store()
        self.retriever = self.store.as_retriever(search_kwargs={"k": 3})

    def add(self, question: str, answer: str) -> None:
        """向量化存入一轮 Q&A。"""
        content = f"用户问题：{question}\n助手回答：{answer}"
        self.store.add_texts(
            [content],
            metadatas=[{"session_id": self.session_id, "type": "qa"}],
        )

    def recall(self, query: str, k: int = 3) -> str:
        """按语义召回相关历史片段。

        优先返回当前 session_id 的片段；无则用全部命中。
        无历史时返回空串（由调用方填入 PROMPT 槽位的"无相关历史记忆"）。
        """
        try:
            docs = self.retriever.invoke(query)
        except Exception:
            return ""

        if not docs:
            return ""

        # 优先当前 session_id
        same_session = [d for d in docs if d.metadata.get("session_id") == self.session_id]
        pool = same_session if same_session else docs
        pool = pool[:k]

        return "\n---\n".join(d.page_content for d in pool)

    def reset(self) -> None:
        """清空记忆集合。

        依据：docs/DESIGN.md §3.3、docs/API.md §3（集合级 drop，容错处理）
        """
        try:
            # Milvus drop_collection 接口
            from pymilvus import connections, utility

            connections.connect(alias="default", uri=str(settings.vector_db_path))
            if utility.has_collection(settings.memory_collection):
                utility.drop_collection(settings.memory_collection)
        except Exception:
            # 集合不存在或其他异常：静默成功（幂等）
            pass


def _lazy_embeddings() -> OpenAIEmbeddings:
    """延迟导入，避免循环依赖。"""
    from .embeddings import get_embeddings

    return get_embeddings()
