"""Markdown 加载与切分：读取本地知识库目录下的 .md 文件。"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import settings


def iter_markdown_files(root: Path) -> Iterator[Path]:
    """递归遍历目录下所有 .md 文件。"""
    if not root.exists():
        return
    for path in sorted(root.rglob("*.md")):
        if path.is_file():
            yield path


def load_documents(root: Path | None = None) -> list[Document]:
    """加载目录下全部 Markdown 为 Document（保留 source 元数据）。"""
    root = root or settings.docs_dir
    docs: list[Document] = []
    for path in iter_markdown_files(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        docs.append(Document(page_content=text, metadata={"source": str(path)}))
    return docs


def split_documents(docs: list[Document]) -> list[Document]:
    """按 Markdown 结构递归切分，保留 source 元数据。"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(docs)


def load_and_split(root: Path | None = None) -> list[Document]:
    """一步：加载 + 切分。"""
    return split_documents(load_documents(root))
