"""CLI command implementations for TEDDI Tool."""

from __future__ import annotations

import asyncio

from teddi_tool.cli import args
from teddi_tool.models import OutputFormat, SearchIn, SearchPattern
from teddi_tool.search_utils import (
    build_results_payload,
    execute_list_bodies,
    execute_search,
    render_table,
    serialize_payload,
)
from teddi_tool.server import main as run_server


def search_term(
    term: args.TermArgument,
    *,
    scope: args.ScopeOption = SearchIn.BOTH,
    pattern: args.PatternOption = "alloccurrences",
    technical_bodies: args.TechnicalBodiesOption = None,
    output: args.OutputOption = OutputFormat.TABLE,
) -> None:
    """Search TEDDI terms with optional scope and pattern filters."""
    request, response = asyncio.run(
        execute_search(term, scope, SearchPattern(pattern), technical_bodies)
    )

    if output is OutputFormat.TABLE:
        render_table(term, response)
    else:
        payload = build_results_payload(request, response)
        print(serialize_payload(payload, output))


def list_bodies() -> None:
    """List available technical bodies in TEDDI."""
    bodies = asyncio.run(execute_list_bodies())
    print("Available Technical Bodies:")
    for body in bodies:
        print(f"  - {body}")


def server() -> None:
    """Start the FastMCP server on stdio."""
    run_server()
