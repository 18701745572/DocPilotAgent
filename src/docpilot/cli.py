"""CLI 入口：index / ask / reset 命令。"""
from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel

from .agent import ask
from .config import settings
from .embeddings import get_embeddings
from .loader import load_and_split
from .memory import PersistentMemory
from .vectorstore import get_docs_store

app = typer.Typer(help="DocPilotAgent - 研发文档助手智能体（只读，不可修改代码）")
console = Console()


@app.command()
def index():
    """索引本地知识库（docs 目录）到 Milvus Lite。"""
    settings.ensure_dirs()
    console.print(f"[cyan]加载知识库：{settings.docs_dir}[/]")
    chunks = load_and_split()
    if not chunks:
        console.print("[yellow]未找到任何 Markdown 文档，请先在 docs/ 放入 .md 文件。[/]")
        raise typer.Exit()
    console.print(f"[cyan]切分为 {len(chunks)} 个片段，写入 Milvus Lite...[/]")
    store = get_docs_store(get_embeddings())
    store.add_documents(chunks)
    console.print(f"[green]索引完成，共写入 {len(chunks)} 个片段。[/]")


@app.command(name="ask")
def ask_cmd(
    question: str = typer.Argument(..., help="要提问的问题"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="显示中间步骤"),
):
    """向智能体提问。"""
    console.print(Panel(question, title="问题", border_style="cyan"))
    answer = ask(question, verbose=verbose)
    console.print(Panel(answer, title="回答", border_style="green"))


@app.command(name="reset")
def reset_cmd():
    """清空跨会话记忆。"""
    PersistentMemory(get_embeddings()).reset()
    console.print("[green]已清空跨会话记忆。[/]")


def main():
    app()


if __name__ == "__main__":
    main()
