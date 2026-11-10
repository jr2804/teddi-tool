"""FastMCP 3.0 server for TEDDI search."""

import logging
from typing import Any

from fastmcp import FastMCP

from teddi_mcp.client import TeddiClient
from teddi_mcp.models import SearchIn, SearchPattern, SearchRequest
from teddi_mcp.search_utils import build_results_payload, parse_technical_bodies

logger = logging.getLogger(__name__)

# Create FastMCP server
server = FastMCP("teddi-mcp")


@server.tool
async def list_technical_bodies() -> dict[str, list[str]]:
    """List supported technical body filters for TEDDI search."""
    async with TeddiClient() as client:
        bodies = await client.get_available_technical_bodies()

    return {"technical_bodies": [tb.value for tb in bodies]}


@server.tool
async def search_teddi(
    term: str,
    search_in: str = SearchIn.BOTH.value,
    search_pattern: str = SearchPattern.ALL_OCCURRENCES.value,
    technical_bodies: str | None = None,
) -> dict[str, Any]:
    """Search TEDDI terms with optional scope and pattern filters.

    Args:
        term: Term or abbreviation to search.
        search_in: One of abbreviations, definitions, both.
        search_pattern: One of exactmatch, startingwith, endingwith, alloccurrences.
        technical_bodies: Optional comma-separated technical body filter.
    """
    try:
        request = SearchRequest(
            term=term,
            search_in=SearchIn(search_in.lower()),
            search_pattern=SearchPattern(search_pattern.lower()),
            technical_bodies=parse_technical_bodies(technical_bodies),
        )
    except ValueError as exc:
        valid_search_in = ", ".join(v.value for v in SearchIn)
        valid_search_pattern = ", ".join(v.value for v in SearchPattern)
        message = (
            "Invalid search arguments. "
            f"search_in must be one of: {valid_search_in}; "
            f"search_pattern must be one of: {valid_search_pattern}."
        )
        raise ValueError(message) from exc

    async with TeddiClient() as client:
        response = await client.search_terms(request)

    return build_results_payload(request, response)


@server.tool
async def get_term_info(
    term: str,
    technical_bodies: str | None = None,
) -> dict[str, Any]:
    """Get exact-match TEDDI entries for one term.

    This helper uses search_in=both and search_pattern=exactmatch.
    """
    request = SearchRequest(
        term=term,
        search_in=SearchIn.BOTH,
        search_pattern=SearchPattern.EXACT_MATCH,
        technical_bodies=parse_technical_bodies(technical_bodies),
    )

    async with TeddiClient() as client:
        response = await client.search_terms(request)

    payload = build_results_payload(request, response)
    payload["exact_match"] = response.total_count > 0
    return payload


def main() -> None:
    """Main entry point for the MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.info("Starting TEDDI-MCP server")

    # Run the server on stdio
    server.run()


if __name__ == "__main__":
    main()
