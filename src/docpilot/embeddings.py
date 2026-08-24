"""嵌入封装：OpenAI 兼容 OpenAIEmbeddings。

依据：docs/DESIGN.md §1、docs/CONFIG.md §1.1
"""

from __future__ import annotations

from langchain_openai import OpenAIEmbeddings

from .config import settings


def get_embeddings() -> OpenAIEmbeddings:
    """返回 OpenAIEmbeddings 实例。缺 API Key 时抛 RuntimeError。"""
    if not settings.openai_api_key:
        raise RuntimeError(
            "未配置 OPENAI_API_KEY，请在 .env 中设置（参考 .env.example）。"
        )
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )
