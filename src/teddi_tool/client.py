"""Core TEDDI client with protocol-based abstraction."""

import logging
from pathlib import Path
from typing import Protocol

import httpx2

from teddi_tool.http_client import create_cached_teddi_async_client
from teddi_tool.models import (
    SearchIn,
    SearchPattern,
    SearchRequest,
    SearchResponse,
)
from teddi_tool.parser import parse_technical_bodies_page, parse_teddi_response

TEDDI_SEARCH_URL = "https://webapp.etsi.org/Teddi/Main.asp"
TEDDI_MENU_URL = "https://webapp.etsi.org/Teddi/Menu.asp"

# Search responses are volatile, so their cached responses expire quickly.
SEARCH_CACHE_TTL = 2 * 60 * 60

# The menu changes rarely, so its cached responses get a generous TTL (90 days).
TEDDI_MENU_CACHE_TTL = 90 * 24 * 60 * 60

# Map enums to TEDDI form parameter values
SEARCH_IN_TO_PARAM = {
    SearchIn.ABBREVIATIONS: 1,
    SearchIn.DEFINITIONS: 2,
    SearchIn.BOTH: 3,
}

SEARCH_PATTERN_TO_PARAM = {
    SearchPattern.EXACT_MATCH: 1,
    SearchPattern.ALL_OCCURRENCES: 2,
    SearchPattern.STARTING_WITH: 3,
    SearchPattern.ENDING_WITH: 4,
}

logger = logging.getLogger(__name__)


class TeddiSource(Protocol):
    """Protocol for TEDDI search sources (enables mocking/substitution)."""

    async def search_terms(self, request: SearchRequest) -> SearchResponse:
        """Search for terms in TEDDI.

        Args:
            request: Search request parameters.

        Returns:
            SearchResponse with matching terms and documents.
        """
        ...

    async def get_available_technical_bodies(self) -> list[str]:
        """Get list of available technical bodies in TEDDI.

        Returns:
            List of technical-body codes supported by TEDDI.
        """
        ...

    async def fetch_document(self, url: str) -> bytes:
        """Fetch document content from URL.

        Args:
            url: Full HTTP URL to document.

        Returns:
            Document content as bytes.

        Raises:
            httpx2.HTTPError: If fetch fails.
        """
        ...


class TeddiClient:
    """Client for querying ETSI TEDDI search engine."""

    def __init__(
        self,
        client: httpx2.AsyncClient | None = None,
        cache_dir: Path | None = None,
        cache_ttl: int = SEARCH_CACHE_TTL,
        menu_cache_ttl: int = TEDDI_MENU_CACHE_TTL,
    ) -> None:
        """Initialize TeddiClient.

        Args:
            client: Optional pre-configured httpx2.AsyncClient (bypasses caching).
            cache_dir: Optional cache directory for HTTP caching.
            cache_ttl: TTL in seconds for cached search responses.
            menu_cache_ttl: TTL in seconds for cached technical-body menus.

        Raises:
            ValueError: If a TTL is not positive.
        """
        if cache_ttl <= 0 or menu_cache_ttl <= 0:
            raise ValueError("Cache TTLs must be positive")
        self._client = client
        self._menu_client: httpx2.AsyncClient | None = None
        self._cache_dir = cache_dir
        self._cache_ttl = cache_ttl
        self._menu_cache_ttl = menu_cache_ttl
        self._owned_client = False

    async def __aenter__(self) -> "TeddiClient":
        """Context manager entry."""
        if self._client is None:
            self._client = await create_cached_teddi_async_client(
                cache_dir=self._cache_dir,
                cache_ttl=self._cache_ttl,
            )
            self._menu_client = await create_cached_teddi_async_client(
                cache_dir=self._cache_dir,
                cache_ttl=self._menu_cache_ttl,
            )
            self._owned_client = True
        return self

    async def __aexit__(self, *args) -> None:
        """Context manager exit."""
        if self._owned_client:
            if self._client:
                await self._client.aclose()
                self._client = None
            if self._menu_client:
                await self._menu_client.aclose()
                self._menu_client = None

    async def search_terms(self, request: SearchRequest) -> SearchResponse:
        """Search for terms in TEDDI.

        Args:
            request: Search request with term and filters.

        Returns:
            SearchResponse with matching terms and documents.

        Raises:
            httpx2.HTTPError: If HTTP request fails.
            ValueError: If response cannot be parsed.
        """
        client = self._get_client()

        # Build form data with TEDDI parameter names
        form_data = {
            "qWhatToSearch": request.term,
            "qWhatOption": SEARCH_IN_TO_PARAM[request.search_in],
            "qWhereOption": SEARCH_PATTERN_TO_PARAM[request.search_pattern],
            "btnSearch.x": 0,
            "btnSearch.y": 0,
        }

        # Add technical bodies filter if specified
        if request.technical_bodies:
            if any(tb.casefold() == "all" for tb in request.technical_bodies):
                form_data["qShowTBs"] = "ALL"
            else:
                form_data["qShowTBs"] = ",".join(request.technical_bodies)
        else:
            form_data["qShowTBs"] = "ALL"

        logger.debug(f"Searching TEDDI: {request.term} with form data: {form_data}")

        # Make request to TEDDI
        response = await client.post(TEDDI_SEARCH_URL, data=form_data)
        response.raise_for_status()

        # Parse HTML response
        results = parse_teddi_response(response.text)

        return SearchResponse(
            query=request,
            results=results,
            total_count=len(results),
        )

    async def get_available_technical_bodies(self) -> list[str]:
        """Get list of available technical bodies from the TEDDI search form.

        Menu responses are cached for ``TEDDI_MENU_CACHE_TTL`` (90 days) in a
        dedicated client, since the list changes rarely. When a client was
        injected, it is used for the menu request as well.

        Returns:
            Technical-body codes accepted by the ``qShowTBs`` filter.

        Raises:
            httpx2.HTTPError: If the menu page cannot be fetched.
            ValueError: If the menu page cannot be parsed.
            RuntimeError: If the client was not initialised.
        """
        menu_client = self._menu_client if self._menu_client is not None else self._get_client()
        return await self._read_technical_bodies(menu_client)

    async def fetch_document(self, url: str) -> bytes:
        """Fetch document content from URL.

        Args:
            url: Full HTTP URL to document.

        Returns:
            Document content as bytes.

        Raises:
            httpx2.HTTPError: If fetch fails.
        """
        client = self._get_client()
        logger.debug(f"Fetching document: {url}")
        response = await client.get(url)
        response.raise_for_status()
        return response.content

    def _get_client(self) -> httpx2.AsyncClient:
        """Get or create client."""
        if self._client is None:
            raise RuntimeError("Client not initialized. Use async with statement.")
        return self._client

    @staticmethod
    async def _read_technical_bodies(client: httpx2.AsyncClient) -> list[str]:
        """Fetch and parse the technical-body menu via ``client``.

        Args:
            client: HTTP client used for the menu request.

        Returns:
            Technical-body codes accepted by the ``qShowTBs`` filter.

        Raises:
            httpx2.HTTPError: If the menu page cannot be fetched.
            ValueError: If the menu page cannot be parsed.
        """
        response = await client.get(TEDDI_MENU_URL)
        response.raise_for_status()
        return parse_technical_bodies_page(response.text)
