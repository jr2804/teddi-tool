"""Core TEDDI client with protocol-based abstraction."""

import logging
from pathlib import Path
from typing import Protocol

import httpx2

from teddi_tool.http_client import create_cached_teddi_async_client
from teddi_tool.models import (
    TECHNICAL_BODY_CODES,
    SearchIn,
    SearchPattern,
    SearchRequest,
    SearchResponse,
)
from teddi_tool.parser import parse_technical_bodies_page, parse_teddi_response

TEDDI_SEARCH_URL = "https://webapp.etsi.org/Teddi/Main.asp"
TEDDI_MENU_URL = "https://webapp.etsi.org/Teddi/Menu.asp"

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
    ) -> None:
        """Initialize TeddiClient.

        Args:
            client: Optional pre-configured httpx2.AsyncClient.
            cache_dir: Optional cache directory for HTTP caching.
        """
        self._client = client
        self._cache_dir = cache_dir
        self._owned_client = False

    async def __aenter__(self) -> "TeddiClient":
        """Context manager entry."""
        if self._client is None:
            self._client = await create_cached_teddi_async_client(cache_dir=self._cache_dir)
            self._owned_client = True
        return self

    async def __aexit__(self, *args) -> None:
        """Context manager exit."""
        if self._owned_client and self._client:
            await self._client.aclose()
            self._client = None

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

        Falls back to the bundled code list when the menu page cannot be
        fetched or parsed.

        Returns:
            Technical-body codes accepted by the ``qShowTBs`` filter.
        """
        client = self._get_client()
        try:
            response = await client.get(TEDDI_MENU_URL)
            response.raise_for_status()
            bodies = parse_technical_bodies_page(response.text)
        except (httpx2.HTTPError, ValueError):
            logger.warning("Falling back to bundled technical-body list")
            return list(TECHNICAL_BODY_CODES)

        return bodies or list(TECHNICAL_BODY_CODES)

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
