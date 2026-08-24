"""跨会话记忆持久化：将历史问答向量化存入 Milvus，按语义相关性检索。

练习点：记忆管理。
- 每轮 Q&A 以一条文档存入 memory 集合；
- 新问题到来时检索语义最相关的历史片段注入上下文；
- 跨进程持久化（Milvus Lite 本地文件）。
"""
from __future__ import annotations

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from .config import settings
from .vectorstore import get_memory_store


class PersistentMemory:
    """基于向量库的跨会话记忆。"""

    def __init__(self, embeddings: Embeddings, session_id: str | None = None):
        self.store = get_memory_store(embeddings)
        self.session_id = session_id or settings.session_id
        self.retriever = self.store.as_retriever(search_kwargs={"k": 3})

    def add(self, question: str, answer: str) -> None:
        """记录一轮问答（向量化持久化）。"""
        content = f"用户问题：{question}\n助手回答：{answer}"
        self.store.add_texts(
            [content],
            metadatas=[{"session_id": self.session_id, "type": "qa"}],
        )

    def recall(self, query: str, k: int = 3) -> str:
        """检索与当前问题相关的历史记忆，返回拼接文本（无历史则空串）。"""
        docs: list[Document] = self.retriever.invoke(query)
        if not docs:
            return ""
        relevant = [d for d in docs if d.metadata.get("session_id") == self.session_id]
        if not relevant:
            relevant = docs
        return "\n---\n".join(d.page_content for d in relevant[:k])

    def reset(self) -> None:
        """清空整个记忆集合。

        注意：Milvus Lite 不便按条件删除单会话记录，这里采用集合级重建，
        会清除所有会话的记忆。生产环境应改用按 session_id 的 delete expr。
        """
        try:
            # langchain_milvus 的底层 pymilvus collection
            col = getattr(self.store, "col", None)
            if col is not None:
                col.drop()
        except Exception:
            # 集合不存在等情形，忽略
            pass
