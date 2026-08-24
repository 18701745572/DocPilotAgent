"""只读工具白名单。

本目录下所有工具均为只读：
- search_docs：检索知识库文档
- read_file：读取白名单目录（docs/logs）内的文件
- search_logs：搜索报错日志

核心约束：本智能体不提供任何写文件 / 执行命令 / 修改代码的工具，
从工具能力层即杜绝对代码库的修改，仅靠提示词约束不可靠。
"""
from .read_file import read_file
from .search_docs import search_docs
from .search_logs import search_logs

# Agent 仅绑定此白名单内的工具
ALL_TOOLS = [search_docs, read_file, search_logs]

__all__ = ["search_docs", "read_file", "search_logs", "ALL_TOOLS"]
