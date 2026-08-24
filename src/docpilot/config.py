"""配置加载：环境变量 → Settings dataclass。

依据：docs/CONFIG.md §1、docs/DESIGN.md §6
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# 模块加载时即读取 .env，确保 settings 单例拿到正确值
load_dotenv(override=False)


@dataclass
class Settings:
    """全部配置项。字段对应 docs/CONFIG.md §1。"""

    # OpenAI 兼容 API
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_base_url: str = field(
        default_factory=lambda: os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    )
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o-mini"))
    embedding_model: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    )

    # 数据源目录
    docs_dir: Path = field(default_factory=lambda: Path(os.getenv("DOCS_DIR", "./docs")))
    logs_dir: Path = field(default_factory=lambda: Path(os.getenv("LOGS_DIR", "./logs")))

    # 向量库（Milvus Lite）
    vector_db_path: Path = field(
        default_factory=lambda: Path(os.getenv("VECTOR_DB_PATH", "./data/docpilot.db"))
    )
    docs_collection: str = field(
        default_factory=lambda: os.getenv("DOCS_COLLECTION", "kb_docs")
    )
    memory_collection: str = field(
        default_factory=lambda: os.getenv("MEMORY_COLLECTION", "kb_memory")
    )

    # 会话
    session_id: str = field(default_factory=lambda: os.getenv("SESSION_ID", "default"))

    # RAG / 切分参数
    retrieval_top_k: int = field(
        default_factory=lambda: int(os.getenv("RETRIEVAL_TOP_K", "4"))
    )
    chunk_size: int = field(default_factory=lambda: int(os.getenv("CHUNK_SIZE", "800")))
    chunk_overlap: int = field(
        default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "120"))
    )

    def ensure_dirs(self) -> None:
        """创建运行时所需目录：data/ 与 docs/。"""
        self.vector_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)


# 模块级单例
settings = Settings()
