"""嵌入模型：OpenAI 兼容 Embeddings，用于文档与会话记忆向量化。"""
from __future__ import annotations

from langchain_openai import OpenAIEmbeddings

from .config import settings


def get_embeddings() -> OpenAIEmbeddings:
    """构造 OpenAI 兼容的嵌入模型。"""
    if not settings.openai_api_key:
        raise RuntimeError(
            "未配置 OPENAI_API_KEY，请在 .env 中设置（参考 .env.example）"
        )
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )
