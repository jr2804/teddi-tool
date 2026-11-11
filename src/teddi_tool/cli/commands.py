"""CLI command implementations for TEDDI Tool."""

from __future__ import annotations

import asyncio

from teddi_tool.cli import args
from teddi_tool.client import SEARCH_CACHE_TTL, TEDDI_MENU_CACHE_TTL
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
    cache_ttl: args.CacheTtlOption = SEARCH_CACHE_TTL,
    menu_cache_ttl: args.MenuCacheTtlOption = TEDDI_MENU_CACHE_TTL,
) -> None:
    """Search TEDDI terms with optional scope and pattern filters."""
    request, response = asyncio.run(
        execute_search(
            term,
            scope,
            SearchPattern(pattern),
            technical_bodies,
            cache_ttl=cache_ttl,
            menu_cache_ttl=menu_cache_ttl,
        )
    )

    if output is OutputFormat.TABLE:
        render_table(term, response)
    else:
        payload = build_results_payload(request, response)
        print(serialize_payload(payload, output))


def list_bodies(
    menu_cache_ttl: args.MenuCacheTtlOption = TEDDI_MENU_CACHE_TTL,
) -> None:
    """List available technical bodies in TEDDI."""
    bodies = asyncio.run(execute_list_bodies(menu_cache_ttl=menu_cache_ttl))
    print("Available Technical Bodies:")
    for body in bodies:
        print(f"  - {body}")


def server(
    cache_ttl: args.CacheTtlOption = SEARCH_CACHE_TTL,
    menu_cache_ttl: args.MenuCacheTtlOption = TEDDI_MENU_CACHE_TTL,
) -> None:
    """Start the FastMCP server on stdio."""
    run_server(cache_ttl=cache_ttl, menu_cache_ttl=menu_cache_ttl)
