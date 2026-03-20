"""Shared search logic for TEDDI CLI commands."""

import asyncio
import json
import logging
from typing import Any

from ison_parser import dumps as ison_dumps
from ison_parser import from_dict as ison_from_dict
from rich.console import Console
from rich.table import Table
from toon_format import encode as toon_encode

from teddi_mcp.client import TeddiClient
from teddi_mcp.models import (
    OutputFormat,
    SearchIn,
    SearchPattern,
    SearchRequest,
    SearchResponse,
    TechnicalBody,
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
                [tb.value for tb in request.technical_bodies] if request.technical_bodies else None
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
) -> tuple[SearchRequest, SearchResponse]:
    """Execute search and return request/response pair."""
    tb_filter: list[TechnicalBody] | None = None
    if tb_filter_str:
        tb_values = [v.strip().lower() for v in tb_filter_str.split(",")]
        tb_filter = [TechnicalBody(v) for v in tb_values]

    request = SearchRequest(
        term=term,
        search_in=search_scope,
        search_pattern=search_pattern,
        technical_bodies=tb_filter,
    )

    async with TeddiClient() as client:
        response = await client.search_terms(request)

    return request, response


async def execute_list_bodies() -> list[TechnicalBody]:
    """Execute list bodies and return technical bodies."""
    async with TeddiClient() as client:
        return await client.get_available_technical_bodies()
