"""CLI 入口：index / ask / reset 三命令。

依据：docs/API.md 全文（命令行为、输出示例、退出码）
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel

from .agent import ask as agent_ask
from .config import settings
from .embeddings import get_embeddings
from .loader import load_and_split
from .memory import PersistentMemory
from .vectorstore import get_docs_store

app = typer.Typer(
    name="docpilot",
    help="DocPilotAgent - 研发文档助手智能体（只读，不可修改代码）",
    no_args_is_help=True,
)
console = Console()


@app.command()
def index() -> None:
    """索引本地知识库到 Milvus Lite。"""
    settings.ensure_dirs()
    console.print(f"加载知识库：{settings.docs_dir}")

    chunks = load_and_split()
    if not chunks:
        console.print("[yellow]未找到任何 Markdown[/yellow]")
        raise typer.Exit(code=1)

    console.print(f"切分为 {len(chunks)} 个片段，写入 Milvus Lite...")
    store = get_docs_store()
    store.add_documents(chunks)
    console.print(f"[green]索引完成，共写入 {len(chunks)} 个片段。[/green]")


@app.command()
def ask(
    question: str = typer.Argument(..., help="要提问的问题"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="显示中间步骤"),
) -> None:
    """向智能体提问。"""
    console.print(Panel(question, title="问题", border_style="cyan"))

    try:
        answer = agent_ask(question, verbose=verbose)
    except RuntimeError as e:
        console.print(f"[red]错误：{e}[/red]")
        raise typer.Exit(code=2) from e
    except Exception as e:
        console.print(f"[red]调用失败：{e}[/red]")
        raise typer.Exit(code=2) from e

    console.print(Panel(answer, title="回答", border_style="green"))


@app.command()
def reset() -> None:
    """清空跨会话记忆。"""
    embeddings = get_embeddings()
    memory = PersistentMemory(embeddings)
    memory.reset()
    console.print("[green]已清空跨会话记忆。[/green]")


def main() -> None:
    """CLI 主入口。"""
    app()


if __name__ == "__main__":
    main()
