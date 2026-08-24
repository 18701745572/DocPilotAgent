"""LLM 封装：OpenAI 兼容 ChatModel。

通过 base_url 可切换到豆包 / DeepSeek / Qwen 等兼容接口。
"""
from __future__ import annotations

from langchain_openai import ChatOpenAI

from .config import settings


def get_llm(temperature: float = 0.2) -> ChatOpenAI:
    """构造一个 OpenAI 兼容的 ChatModel。"""
    if not settings.openai_api_key:
        raise RuntimeError(
            "未配置 OPENAI_API_KEY，请在 .env 中设置（参考 .env.example）"
        )
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        temperature=temperature,
    )
