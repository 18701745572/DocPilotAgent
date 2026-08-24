"""LLM 封装：OpenAI 兼容 ChatOpenAI。

依据：docs/DESIGN.md §1、docs/CONFIG.md §1.1
"""

from __future__ import annotations

from langchain_openai import ChatOpenAI

from .config import settings


def get_llm(temperature: float = 0.2) -> ChatOpenAI:
    """返回 ChatOpenAI 实例。缺 API Key 时抛 RuntimeError。

    依据：docs/ROADMAP.md P1 验收
    """
    if not settings.openai_api_key:
        raise RuntimeError(
            "未配置 OPENAI_API_KEY，请在 .env 中设置（参考 .env.example）。"
        )
    return ChatOpenAI(
        model=settings.llm_model,
        temperature=temperature,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )
