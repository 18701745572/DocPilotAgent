"""Markdown 加载与切分。

依据：docs/DESIGN.md §3.1、docs/CONFIG.md §5.1、docs/DATA_CURATION.md §2.4
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import settings


def iter_markdown_files(root: Path) -> Iterator[Path]:
    """递归遍历 root 下所有 .md 文件。"""
    yield from root.rglob("*.md")


def load_documents(root: Path | None = None) -> list[Document]:
    """加载 root 下所有 .md 为 Document，metadata 含 source。

    依据：docs/CONFIG.md §5.1（编码 UTF-8，metadata.source=文件绝对路径）
    """
    root = root or settings.docs_dir
    docs: list[Document] = []
    for path in iter_markdown_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        docs.append(Document(page_content=text, metadata={"source": str(path)}))
    return docs


def split_documents(docs: list[Document]) -> list[Document]:
    """按 Markdown 结构切分。

    分隔符优先级：## > ### > 段落 > 行 > 空格
    依据：docs/CONFIG.md §5.1
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(docs)


def load_and_split(root: Path | None = None) -> list[Document]:
    """一步：加载 + 切分。"""
    return split_documents(load_documents(root))
