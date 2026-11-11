"""Shared search logic for TEDDI CLI commands."""

import json
import logging
from typing import Any

from ison_parser import dumps as ison_dumps
from ison_parser import from_dict as ison_from_dict
from rich.console import Console
from rich.table import Table
from toon_format import encode as toon_encode

from teddi_tool.client import SEARCH_CACHE_TTL, TEDDI_MENU_CACHE_TTL, TeddiClient
from teddi_tool.models import (
    OutputFormat,
    SearchIn,
    SearchPattern,
    SearchRequest,
    SearchResponse,
)

console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def build_results_payload(request: SearchRequest, response: SearchResponse) -> dict[str, Any]:
    """Build canonical machine-readable payload for non-table outputs."""
    return {
        "query": {
            "term": request.term,
            "search_in": request.search_in.value,
            "search_pattern": request.search_pattern.value,
            "technical_bodies": (
                list(request.technical_bodies) if request.technical_bodies else None
            ),
        },
        "total_count": response.total_count,
        "results": [
            {
                "term": result.term,
                "description": result.description,
                "documents": [
                    {
                        "technical_body": doc.technical_body,
                        "specification": doc.specification,
                        "url": doc.url,
                    }
                    for doc in result.documents
                ],
            }
            for result in response.results
        ],
    }


def serialize_payload(payload: dict[str, Any], output: OutputFormat) -> str:
    """Serialize payload according to requested output format."""
    if output == OutputFormat.JSON:
        return json.dumps(payload, indent=2)

    if output == OutputFormat.ISON:
        return str(ison_dumps(ison_from_dict(payload)))

    if output == OutputFormat.TOON:
        return str(toon_encode(payload))

    raise RuntimeError(f"Unsupported output format: {output.value}")


def render_table(term: str, response: SearchResponse) -> None:
    """Render search response as a Rich table."""
    if not response.results:
        console.print("[yellow]No results found[/yellow]")
        return

    table = Table(title=f"TEDDI Search Results: '{term}' ({response.total_count})")
    table.add_column("Term", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Technical Body", style="green")
    table.add_column("Specification", style="blue")

    for result in response.results:
        first_doc = True
        for doc in result.documents:
            table.add_row(
                result.term if first_doc else "",
                result.description if first_doc else "",
                doc.technical_body,
                doc.specification,
            )
            first_doc = False

        if not result.documents:
            table.add_row(
                result.term,
                result.description,
                "[yellow]No documents[/yellow]",
                "",
            )

    console.print(table)


async def execute_search(
    term: str,
    search_scope: SearchIn,
    search_pattern: SearchPattern,
    tb_filter_str: str | None,
    *,
    cache_ttl: int = SEARCH_CACHE_TTL,
    menu_cache_ttl: int = TEDDI_MENU_CACHE_TTL,
) -> tuple[SearchRequest, SearchResponse]:
    """Execute search and return request/response pair.

    The technical-body list advertised by TEDDI is fetched through the cached
    client whenever a filter is given, so new codes are picked up without a
    release; a failed menu fetch aborts the search.

    Args:
        term: Search term.
        search_scope: Where to search inside each entry.
        search_pattern: How the term must occur.
        tb_filter_str: Optional comma-separated technical-body filter.
        cache_ttl: TTL in seconds for cached search responses.
        menu_cache_ttl: TTL in seconds for cached technical-body menus.

    Returns:
        The canonical request plus the parsed response.

    Raises:
        httpx2.HTTPError: If the menu (with a filter) or search request fails.
        ValueError: If an unknown technical body is requested.
    """
    async with TeddiClient(
        cache_ttl=cache_ttl,
        menu_cache_ttl=menu_cache_ttl,
    ) as client:
        if tb_filter_str:
            known = await client.get_available_technical_bodies()
            technical_bodies = parse_technical_bodies(tb_filter_str, known)
        else:
            technical_bodies = parse_technical_bodies(tb_filter_str, [])
        request = SearchRequest(
            term=term,
            search_in=search_scope,
            search_pattern=search_pattern,
            technical_bodies=technical_bodies,
        )
        response = await client.search_terms(request)

    return request, response


def parse_technical_bodies(tb_filter_str: str | None, known_bodies: list[str]) -> list[str] | None:
    """Parse a comma-separated technical-body filter into canonical codes.

    Matching is case-insensitive against the codes TEDDI currently advertises
    (``known_bodies``); values are normalised to the published casing.

    Args:
        tb_filter_str: Optional comma-separated list (e.g. ``"3GPP,stq"``).
        known_bodies: Codes currently advertised by TEDDI (cached menu list).

    Returns:
        Canonical technical-body codes, or None when the filter is empty.

    Raises:
        ValueError: If any entry is not a known technical body.
    """
    if not tb_filter_str:
        return None

    values = [value.strip() for value in tb_filter_str.split(",") if value.strip()]
    if not values:
        return None

    lookup = {code.casefold(): code for code in known_bodies}
    lookup["all"] = "ALL"

    parsed: list[str] = []
    for value in values:
        code = lookup.get(value.casefold())
        if code is None:
            valid = ", ".join(known_bodies)
            raise ValueError(f"Invalid technical body '{value}'. Supported values: {valid}, ALL")
        parsed.append(code)

    return parsed


async def execute_list_bodies(menu_cache_ttl: int = TEDDI_MENU_CACHE_TTL) -> list[str]:
    """Fetch the technical-body codes TEDDI currently advertises.

    Args:
        menu_cache_ttl: TTL in seconds for the cached technical-body menu.

    Returns:
        Technical-body codes (cached for `menu_cache_ttl` seconds).
    """
    async with TeddiClient(menu_cache_ttl=menu_cache_ttl) as client:
        return await client.get_available_technical_bodies()
