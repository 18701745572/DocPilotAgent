"""只读工具白名单。

不提供任何写文件/执行命令工具。
依据：docs/TOOLS.md §0、ADR-0001-tool-allowlist-over-prompt.md
"""

from .read_file import read_file
from .search_docs import search_docs
from .search_logs import search_logs

__all__ = ["search_docs", "read_file", "search_logs", "ALL_TOOLS"]

# 工具白名单：仅 3 个只读工具
ALL_TOOLS = [search_docs, read_file, search_logs]
