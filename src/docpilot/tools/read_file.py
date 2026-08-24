"""工具：读取本地文件内容（只读，不可写/不可执行）。

练习点：输出权限约束。
仅允许读取知识库目录（docs）与日志目录（logs）下的文件，
从工具层即禁止访问源代码或任意系统文件。
"""
from __future__ import annotations

from pathlib import Path

from langchain_core.tools import tool

from ..config import settings

# 允许读取的根目录白名单
_ALLOWED_ROOTS = [settings.docs_dir, settings.logs_dir]


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


@tool
def read_file(file_path: str) -> str:
    """读取指定文件的内容（只读）。

    仅允许读取知识库目录与日志目录下的文件。
    file_path 可为相对 DOCS_DIR/LOGS_DIR 的路径，或这些目录内的绝对路径。
    """
    p = Path(file_path).expanduser()

    if not p.is_absolute():
        # 相对路径：先在 docs 再在 logs 下尝试
        for root in _ALLOWED_ROOTS:
            candidate = (root / file_path).resolve()
            if _is_within(candidate, root.resolve()) and candidate.exists():
                p = candidate
                break
        else:
            return f"未找到文件：{file_path}"

    p = p.resolve()
    allowed = [r.resolve() for r in _ALLOWED_ROOTS if r.exists()]
    if not any(_is_within(p, root) for root in allowed):
        return f"拒绝访问：{file_path} 不在允许的目录（docs/logs）内。"
    if not p.exists() or not p.is_file():
        return f"文件不存在：{file_path}"
    return p.read_text(encoding="utf-8", errors="ignore")
