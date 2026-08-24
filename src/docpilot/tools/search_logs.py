"""工具：在日志目录中按关键词搜索报错日志（只读）。"""
from __future__ import annotations

import re
from pathlib import Path

from langchain_core.tools import tool

from ..config import settings


@tool
def search_logs(keyword: str, max_results: int = 20) -> str:
    """在报错日志目录中按关键词搜索匹配行。

    keyword：搜索关键词（如错误码、异常类名、报错信息片段）。
    返回匹配的日志行，含文件名与行号。
    """
    logs_dir: Path = settings.logs_dir
    if not logs_dir.exists():
        return f"日志目录不存在：{logs_dir}"
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    hits: list[str] = []
    for path in sorted(logs_dir.rglob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if pattern.search(line):
                hits.append(f"{path}:{lineno}: {line.strip()}")
                if len(hits) >= max_results:
                    hits.append(f"...（已达到上限 {max_results} 条）")
                    return "\n".join(hits)
    if not hits:
        return f"未在日志中找到关键词：{keyword}"
    return "\n".join(hits)
