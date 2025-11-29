#!/usr/bin/env python3
"""SPB Search - Command-line interface for hybrid code search.

A human-friendly CLI tool that combines semantic search (Gemini) with literal
search (ripgrep) for intelligent code discovery.

Usage Examples:
    # Conceptual search (uses Gemini + ripgrep)
    spb search "how does authentication work"

    # With filters
    spb search "error handling" --path src/api --lang python

    # Literal search only (bypasses Gemini)
    spb search --literal "TODO: fix"

    # Semantic search only (Gemini only)
    spb search --semantic "billing patterns"

    # Output formats
    spb search "billing" --format json
    spb search "billing" --format markdown

    # Limit results
    spb search "config" --limit 5

Dependencies:
    - typer: CLI framework
    - rich: Terminal formatting
    - adws.adw_modules.gemini_search: Hybrid search backend
"""

import json
import sys
from pathlib import Path
from typing import Optional

try:
    import typer
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.syntax import Syntax
except ImportError:
    print("Error: Required dependencies not installed.")
    print("Please install: pip install typer rich")
    sys.exit(1)

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from adws.adw_modules.gemini_search import (
    HybridSearchClient,
    quick_search,
    semantic_search,
    literal_search,
    QueryType,
    SearchResult,
    Snippet,
)

app = typer.Typer(
    help="SPB Search - Hybrid code search combining semantic (Gemini) and literal (ripgrep) search",
    add_completion=False,
)
console = Console()


def format_table_output(result: SearchResult, limit: int) -> None:
    """Format search results as a rich table.

    Args:
        result: The search result to format
        limit: Maximum number of results to display
    """
    # Header info
    query_type_emoji = {
        QueryType.CONCEPTUAL: "🧠",
        QueryType.LITERAL: "🔍",
        QueryType.HYBRID: "⚡",
    }

    emoji = query_type_emoji.get(result.query_type, "❓")
    sources = ", ".join(result.sources_used) if result.sources_used else "none"

    header_text = (
        f"Query: [bold cyan]{result.query}[/bold cyan]\n"
        f"Type: [yellow]{emoji} {result.query_type.value.upper()}[/yellow] | "
        f"Sources: [green]{sources}[/green] | "
        f"Results: [blue]{len(result.snippets)}[/blue]"
    )

    console.print(Panel(header_text, title="Search Results", border_style="blue"))

    if not result.snippets:
        console.print("[yellow]No results found.[/yellow]")
        return

    # Create table
    table = Table(show_header=True, header_style="bold magenta", box=None)
    table.add_column("#", style="dim", width=3)
    table.add_column("File", style="cyan", no_wrap=False)
    table.add_column("Line", justify="right", width=6)
    table.add_column("Source", width=8)
    table.add_column("Preview", no_wrap=False)

    # Add rows
    for i, snippet in enumerate(result.snippets[:limit], 1):
        # Truncate file path if too long
        file_path = snippet.file_path
        if len(file_path) > 50:
            file_path = "..." + file_path[-47:]

        # Format line number
        line_num = str(snippet.line_start) if snippet.line_start else "-"

        # Truncate preview
        preview = snippet.content.strip()
        if len(preview) > 80:
            preview = preview[:77] + "..."
        # Remove newlines for preview
        preview = preview.replace("\n", " ")

        # Source badge
        source_styles = {
            "gemini": "[blue]gemini[/blue]",
            "ripgrep": "[green]ripgrep[/green]",
            "merged": "[yellow]merged[/yellow]",
        }
        source = source_styles.get(snippet.source, snippet.source)

        table.add_row(
            str(i),
            file_path,
            line_num,
            source,
            preview
        )

    console.print(table)


def format_json_output(result: SearchResult, limit: int) -> None:
    """Format search results as JSON.

    Args:
        result: The search result to format
        limit: Maximum number of results to include
    """
    output = {
        "query": result.query,
        "query_type": result.query_type.value,
        "sources_used": result.sources_used,
        "total_results": len(result.snippets),
        "success": result.success,
        "snippets": [
            {
                "file_path": s.file_path,
                "content": s.content,
                "line_start": s.line_start,
                "line_end": s.line_end,
                "score": s.score,
                "source": s.source,
                "metadata": s.metadata,
            }
            for s in result.snippets[:limit]
        ]
    }

    if result.error_message:
        output["error"] = result.error_message

    console.print(json.dumps(output, indent=2))


def format_markdown_output(result: SearchResult, limit: int) -> None:
    """Format search results as markdown.

    Args:
        result: The search result to format
        limit: Maximum number of results to include
    """
    # Header
    output = [
        f"# Search Results: {result.query}",
        f"",
        f"- **Query Type**: {result.query_type.value}",
        f"- **Sources Used**: {', '.join(result.sources_used) if result.sources_used else 'none'}",
        f"- **Results Found**: {len(result.snippets)}",
        f"",
    ]

    if not result.snippets:
        output.append("No results found.")
    else:
        output.append("## Results")
        output.append("")

        for i, snippet in enumerate(result.snippets[:limit], 1):
            # Format snippet
            line_info = f":{snippet.line_start}" if snippet.line_start else ""
            source_badge = f"[{snippet.source}]"

            output.extend([
                f"### {i}. `{snippet.file_path}{line_info}` {source_badge}",
                f"",
                "```",
                snippet.content,
                "```",
                "",
            ])

    console.print("\n".join(output))


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query (natural language or pattern)"),
    literal: bool = typer.Option(False, "--literal", "-l", help="Force literal search (ripgrep only)"),
    semantic: bool = typer.Option(False, "--semantic", "-s", help="Force semantic search (Gemini only)"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Filter by path prefix (e.g., 'src/api')"),
    lang: Optional[str] = typer.Option(None, "--lang", help="Filter by language (python, javascript, etc.)"),
    limit: int = typer.Option(10, "--limit", "-n", help="Maximum number of results"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, json, markdown"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose debug output"),
) -> None:
    """Execute a hybrid code search.

    The tool automatically determines the best search strategy based on your query:
    - Conceptual queries → Semantic search (Gemini)
    - Literal patterns → Exact search (ripgrep)
    - Ambiguous queries → Hybrid search (both)

    You can force a specific search mode with --literal or --semantic flags.
    """
    # Configure logging
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    try:
        # Determine search mode
        if literal and semantic:
            console.print("[red]Error: Cannot use both --literal and --semantic flags[/red]")
            raise typer.Exit(1)

        # Execute search based on mode
        if literal:
            # Literal-only search
            client = HybridSearchClient()
            snippets = client.search_ripgrep(
                query,
                path=path,
                file_type=client._language_to_type(lang),
                limit=limit
            )

            # Convert to SearchResult for consistent formatting
            result = SearchResult(
                query=query,
                query_type=QueryType.LITERAL,
                snippets=snippets,
                success=len(snippets) > 0,
                sources_used=["ripgrep"] if snippets else []
            )

        elif semantic:
            # Semantic-only search
            client = HybridSearchClient()

            if not client.gemini_enabled:
                console.print("[red]Error: Gemini search not available.[/red]")
                console.print("Make sure GEMINI_API_KEY is set and index is created.")
                raise typer.Exit(1)

            # Build metadata filter
            metadata_parts = []
            if path:
                metadata_parts.append(f'path_prefix = "{path}"')
            if lang:
                metadata_parts.append(f'language = "{lang}"')
            metadata_filter = " AND ".join(metadata_parts) if metadata_parts else None

            snippets = client.search_gemini(
                query,
                metadata_filter=metadata_filter,
                limit=limit
            )

            # Convert to SearchResult for consistent formatting
            result = SearchResult(
                query=query,
                query_type=QueryType.CONCEPTUAL,
                snippets=snippets,
                success=len(snippets) > 0,
                sources_used=["gemini"] if snippets else []
            )

        else:
            # Hybrid search (default)
            client = HybridSearchClient()
            result = client.hybrid_search(
                query,
                path_filter=path,
                language_filter=lang,
                limit=limit
            )

        # Check for fallback scenarios
        if not result.success:
            if "gemini" not in result.sources_used:
                console.print("[yellow]Note: Gemini search unavailable, using ripgrep only[/yellow]")

        # Format output
        if format == "json":
            format_json_output(result, limit)
        elif format == "markdown":
            format_markdown_output(result, limit)
        else:  # table (default)
            format_table_output(result, limit)

        # Exit with appropriate code
        if not result.snippets:
            raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Search interrupted[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def stats() -> None:
    """Show search backend status and statistics."""
    try:
        client = HybridSearchClient()

        # Check backend availability
        table = Table(title="SPB Search Backend Status", show_header=True, header_style="bold cyan")
        table.add_column("Backend", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details")

        # Gemini status
        if client.gemini_enabled:
            gemini_status = "[green]✓ Available[/green]"
            gemini_details = f"Store: {client._store_name}"
        else:
            gemini_status = "[red]✗ Unavailable[/red]"
            gemini_details = "Check GEMINI_API_KEY and index"

        table.add_row("Gemini File Search", gemini_status, gemini_details)

        # Ripgrep status
        try:
            import subprocess
            result = subprocess.run(["rg", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                rg_status = "[green]✓ Available[/green]"
                rg_details = version
            else:
                rg_status = "[red]✗ Unavailable[/red]"
                rg_details = "Not found"
        except Exception:
            rg_status = "[red]✗ Unavailable[/red]"
            rg_details = "Not installed"

        table.add_row("ripgrep", rg_status, rg_details)

        # Project info
        table.add_row("Project Root", "[blue]ℹ[/blue]", client.project_root)
        table.add_row("State File", "[blue]ℹ[/blue]", client.state_file)

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error checking status: {e}[/red]")
        raise typer.Exit(1)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
