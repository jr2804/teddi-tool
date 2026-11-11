"""FastMCP server for TEDDI search."""

import logging
import os
from typing import Any

from fastmcp import FastMCP

from teddi_tool.client import SEARCH_CACHE_TTL, TEDDI_MENU_CACHE_TTL, TeddiClient
from teddi_tool.models import SearchIn, SearchPattern
from teddi_tool.search_utils import build_results_payload, execute_search

logger = logging.getLogger(__name__)

# Create FastMCP server
server = FastMCP("teddi-tool")

# Cache lifetimes in seconds, configurable via `main()` or environment
# variables (TEDDI_TOOL_CACHE_TTL / TEDDI_TOOL_MENU_CACHE_TTL).
_cache_ttls = {"cache_ttl": SEARCH_CACHE_TTL, "menu_cache_ttl": TEDDI_MENU_CACHE_TTL}


@server.tool
async def list_technical_bodies() -> dict[str, list[str]]:
    """List supported technical body filters for TEDDI search."""
    async with TeddiClient(menu_cache_ttl=_cache_ttls["menu_cache_ttl"]) as client:
        bodies = await client.get_available_technical_bodies()

    return {"technical_bodies": bodies}


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
        scope = SearchIn(search_in.lower())
        pattern = SearchPattern(search_pattern.lower())
    except ValueError as exc:
        valid_search_in = ", ".join(v.value for v in SearchIn)
        valid_search_pattern = ", ".join(v.value for v in SearchPattern)
        message = (
            "Invalid search arguments. "
            f"search_in must be one of: {valid_search_in}; "
            f"search_pattern must be one of: {valid_search_pattern}."
        )
        raise ValueError(message) from exc

    request, response = await execute_search(
        term,
        scope,
        pattern,
        technical_bodies,
        cache_ttl=_cache_ttls["cache_ttl"],
        menu_cache_ttl=_cache_ttls["menu_cache_ttl"],
    )
    return build_results_payload(request, response)


@server.tool
async def get_term_info(
    term: str,
    technical_bodies: str | None = None,
) -> dict[str, Any]:
    """Get exact-match TEDDI entries for one term.

    This helper uses search_in=both and search_pattern=exactmatch.
    """
    request, response = await execute_search(
        term,
        SearchIn.BOTH,
        SearchPattern.EXACT_MATCH,
        technical_bodies,
        cache_ttl=_cache_ttls["cache_ttl"],
        menu_cache_ttl=_cache_ttls["menu_cache_ttl"],
    )

    payload = build_results_payload(request, response)
    payload["exact_match"] = response.total_count > 0
    return payload


def main(cache_ttl: int | None = None, menu_cache_ttl: int | None = None) -> None:
    """Main entry point for the MCP server.

    Args:
        cache_ttl: Search cache TTL in seconds; defaults to the
            `TEDDI_TOOL_CACHE_TTL` environment variable or 2 hours.
        menu_cache_ttl: Technical-body menu cache TTL in seconds; defaults to
            the `TEDDI_TOOL_MENU_CACHE_TTL` environment variable or 90 days.
    """
    _cache_ttls["cache_ttl"] = (
        _ttl_from_env("TEDDI_TOOL_CACHE_TTL", SEARCH_CACHE_TTL) if cache_ttl is None else cache_ttl
    )
    _cache_ttls["menu_cache_ttl"] = (
        _ttl_from_env("TEDDI_TOOL_MENU_CACHE_TTL", TEDDI_MENU_CACHE_TTL)
        if menu_cache_ttl is None
        else menu_cache_ttl
    )
    logger.info(
        "Starting TEDDI MCP server (search cache TTL %ss, menu cache TTL %ss)",
        _cache_ttls["cache_ttl"],
        _cache_ttls["menu_cache_ttl"],
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run the server on stdio
    server.run()


def _ttl_from_env(env_var: str, default: int) -> int:
    """Read a TTL from the environment, falling back to `default`."""
    raw = os.environ.get(env_var)
    if raw is None or not raw.strip():
        return default
    ttl = int(raw)
    if ttl <= 0:
        raise ValueError(f"{env_var} must be a positive number of seconds")
    return ttl


if __name__ == "__main__":
    main()
