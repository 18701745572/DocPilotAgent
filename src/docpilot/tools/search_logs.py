"""search_logs 工具：在 logs/ 中按关键词搜索。

依据：docs/TOOLS.md §3（含返回格式与错误模式）
"""

from __future__ import annotations

import re

from langchain_core.tools import tool

from ..config import settings


@tool
def search_logs(keyword: str, max_results: int = 20) -> str:
    """在报错日志目录中按关键词搜索匹配行。

    keyword 为错误码/异常类名/报错片段，大小写不敏感。
    """
    logs_dir = settings.logs_dir
    if not logs_dir.exists():
        return f"日志目录不存在：{logs_dir}"

    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    hits: list[str] = []

    for path in logs_dir.rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if pattern.search(line):
                hits.append(f"{path}:{lineno}: {line.strip()}")
                if len(hits) >= max_results:
                    hits.append(f"...（已达到上限 {max_results} 条）")
                    return "\n".join(hits)

    if not hits:
        return f"未在日志中找到关键词：{keyword}"

    return "\n".join(hits)
