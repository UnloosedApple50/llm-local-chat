"""CLI interface for LLM Local Chat."""

from __future__ import annotations

import asyncio
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from llm_local_chat.core.client import OllamaClient

app = typer.Typer(
    name="llm-chat",
    help="Local LLM chat — optimized for low-end PCs",
    no_args_is_help=True,
)
console = Console()


@app.command()
def start(
    host: str = typer.Option("http://localhost:11434", "--host", "-h", help="Ollama host"),
    model: str = typer.Option("qwen2.5:12b", "--model", "-m", help="Model to use"),
    port: int = typer.Option(8080, "--port", "-p", help="Web server port"),
):
    """Start the web server."""
    console.print(Panel.fit("[bold blue]LLM Local Chat[/bold blue]"))
    console.print(f"Model: [green]{model}[/green]")
    console.print(f"Host: [green]{host}[/green]")
    console.print(f"Port: [green]{port}[/green]")
    console.print(f"\n[bold]Starting web server...[/bold]")
    console.print(f"Open [blue]http://localhost:{port}[/blue] in your browser\n")

    import uvicorn
    from llm_local_chat.web.server import app as web_app

    uvicorn.run(web_app, host="0.0.0.0", port=port)


@app.command()
def list_models(
    host: str = typer.Option("http://localhost:11434", "--host", "-h", help="Ollama host"),
):
    """List available models."""
    async def _list():
        client = OllamaClient(host=host)
        try:
            models = await client.list_models()
            if not models:
                console.print("[yellow]No models found. Pull one with:[/yellow]")
                console.print("  ollama pull qwen2.5:12b")
                return

            table = Table(title="Available Models")
            table.add_column("Name", style="cyan")
            table.add_column("Size", justify="right")
            table.add_column("Modified")

            for m in models:
                size_gb = m.get("size", 0) / 1e9
                table.add_row(
                    m.get("name", "unknown"),
                    f"{size_gb:.1f} GB",
                    m.get("modified_at", "unknown")[:10],
                )

            console.print(table)
        finally:
            await client.close()

    asyncio.run(_list())


@app.command()
def chat(
    message: str = typer.Argument(..., help="Message to send"),
    host: str = typer.Option("http://localhost:11434", "--host", "-h", help="Ollama host"),
    model: str = typer.Option("qwen2.5:12b", "--model", "-m", help="Model to use"),
    system: Optional[str] = typer.Option(None, "--system", "-s", help="System prompt"),
):
    """Send a single message and get response."""
    async def _chat():
        client = OllamaClient(host=host, model=model)
        try:
            console.print(f"[bold blue]You:[/bold blue] {message}\n")
            console.print("[bold green]Assistant:[/bold green]")

            async for resp in client.chat(
                messages=[{"role": "user", "content": message}],
                system_prompt=system,
                stream=True,
            ):
                console.print(resp.content, end="")
            console.print()
        finally:
            await client.close()

    asyncio.run(_chat())


@app.command()
def pull(
    model: str = typer.Argument("qwen2.5:12b", help="Model to pull"),
    host: str = typer.Option("http://localhost:11434", "--host", "-h", help="Ollama host"),
):
    """Pull a model from Ollama."""
    console.print(f"[yellow]Pulling {model}...[/yellow]")
    console.print("[dim]This may take a while for large models.[/dim]")

    import subprocess
    result = subprocess.run(
        ["ollama", "pull", model],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        console.print(f"[green]✅ Model {model} pulled successfully![/green]")
    else:
        console.print(f"[red]❌ Failed to pull model:[/red]")
        console.print(result.stderr)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
