"""Typer CLI for TEDDI search commands only (teddi-cli executable)."""

import asyncio

import typer

from teddi_mcp.args import (
    OutputOption,
    PatternOption,
    ScopeOption,
    TechnicalBodiesOption,
    TermArgument,
)
from teddi_mcp.models import OutputFormat, SearchIn, SearchPattern
from teddi_mcp.search_utils import (
    build_results_payload,
    execute_list_bodies,
    execute_search,
    render_table,
    serialize_payload,
)

# Search-only app for `teddi-cli` command
search_app = typer.Typer(help="TEDDI Search CLI")


@search_app.command("term")
def search_term(
    term: TermArgument,
    scope: ScopeOption = SearchIn.BOTH,
    pattern: PatternOption = SearchPattern.ALL_OCCURRENCES,
    technical_bodies: TechnicalBodiesOption = None,
    output: OutputOption = OutputFormat.TABLE,
) -> None:
    """Search for a term in TEDDI."""
    request, response = asyncio.run(execute_search(term, scope, pattern, technical_bodies))

    if output == OutputFormat.TABLE:
        render_table(term, response)
    else:
        payload = build_results_payload(request, response)
        print(serialize_payload(payload, output))


@search_app.command("list-bodies")
def list_bodies() -> None:
    """List available technical bodies in TEDDI."""
    bodies = asyncio.run(execute_list_bodies())
    print("Available Technical Bodies:")
    for tb in bodies:
        print(f"  - {tb.value}")


def run() -> None:
    """Entry point for teddi-cli executable."""
    search_app()


if __name__ == "__main__":
    search_app()
