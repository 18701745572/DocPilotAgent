"""read_file 工具：读取白名单内文件。

依据：docs/TOOLS.md §2、ADR-0004-path-allowlist.md、docs/SECURITY.md §2 L3
"""

from __future__ import annotations

from pathlib import Path

from langchain_core.tools import tool

from ..config import settings


def _is_within(path: Path, root: Path) -> bool:
    """校验 path 是否位于 root 内（基于 resolve 后路径）。"""
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _allowed_roots() -> list[Path]:
    """已 resolve 的白名单根（仅含存在的目录）。"""
    return [
        r.resolve()
        for r in (settings.docs_dir, settings.logs_dir)
        if r.exists()
    ]


@tool
def read_file(file_path: str) -> str:
    """读取指定文件的内容（只读）。仅允许读取 docs 与 logs 目录。

    file_path 可为相对路径（优先在 docs/ 与 logs/ 下查找），或绝对路径。
    """
    # 符号链接拒绝（docs/SECURITY.md §6 已知缺口补丁）
    raw = Path(file_path).expanduser()
    if raw.is_symlink():
        return f"拒绝访问：{file_path} 是符号链接，不在允许的目录（docs/logs）内。"

    # 相对路径：在 docs/ 与 logs/ 下查找
    if not raw.is_absolute():
        for root in _allowed_roots():
            candidate = (root / file_path).resolve()
            if _is_within(candidate, root) and candidate.exists() and candidate.is_file():
                return candidate.read_text(encoding="utf-8", errors="ignore")
        return f"未找到文件：{file_path}"

    # 绝对路径：必须在白名单根内
    p = raw.resolve()
    allowed = _allowed_roots()
    if not any(_is_within(p, root) for root in allowed):
        return f"拒绝访问：{file_path} 不在允许的目录（docs/logs）内。"

    if not p.exists() or not p.is_file():
        return f"文件不存在：{file_path}"

    return p.read_text(encoding="utf-8", errors="ignore")
