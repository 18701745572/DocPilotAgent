"""配置加载：从环境变量（.env）读取所有运行参数。"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


@dataclass
class Settings:
    """运行配置。所有字段均可由环境变量覆盖。"""

    # OpenAI 兼容
    openai_api_key: str = field(default_factory=lambda: _env("OPENAI_API_KEY"))
    openai_base_url: str = field(
        default_factory=lambda: _env("OPENAI_BASE_URL", "https://api.openai.com/v1")
    )
    llm_model: str = field(default_factory=lambda: _env("LLM_MODEL", "gpt-4o-mini"))
    embedding_model: str = field(
        default_factory=lambda: _env("EMBEDDING_MODEL", "text-embedding-3-small")
    )

    # 数据源目录
    docs_dir: Path = field(default_factory=lambda: Path(_env("DOCS_DIR", "./docs")))
    logs_dir: Path = field(default_factory=lambda: Path(_env("LOGS_DIR", "./logs")))

    # 向量库（Milvus Lite 本地文件）
    vector_db_path: Path = field(
        default_factory=lambda: Path(_env("VECTOR_DB_PATH", "./data/docpilot.db"))
    )
    docs_collection: str = field(
        default_factory=lambda: _env("DOCS_COLLECTION", "kb_docs")
    )
    memory_collection: str = field(
        default_factory=lambda: _env("MEMORY_COLLECTION", "kb_memory")
    )

    # 会话
    session_id: str = field(default_factory=lambda: _env("SESSION_ID", "default"))

    # RAG / 切分参数
    retrieval_top_k: int = 4
    chunk_size: int = 800
    chunk_overlap: int = 120

    def ensure_dirs(self) -> None:
        """创建必要的运行时目录。"""
        self.vector_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
