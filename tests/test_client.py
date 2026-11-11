"""Tests for TeddiClient."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from src.teddi_tool.client import TeddiClient
from src.teddi_tool.models import SearchIn, SearchPattern, SearchRequest


@pytest.mark.asyncio
class TestTeddiClient:
    """Test TeddiClient search functionality."""

    async def test_search_terms_basic(self) -> None:
        """Test basic term search."""
        mock_html = """
        <table>
            <tr><th>Term</th><th>Description</th><th>Declared in document(s)</th></tr>
            <tr>
                <td>QoS</td>
                <td>Quality of Service</td>
                <td>
                    <table>
                        <tr><td>3GPP</td><td><a href="/specs/ts-24-008">TS 24.008</a></td></tr>
                    </table>
                </td>
            </tr>
        </table>
        """

        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.text = mock_html
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response

        client = TeddiClient(client=mock_client)
        request = SearchRequest(term="QoS")
        response = await client.search_terms(request)

        assert response.total_count == 1
        assert len(response.results) == 1
        assert response.results[0].term == "QoS"
        assert response.results[0].description == "Quality of Service"

    async def test_search_with_filters(self) -> None:
        """Test search with custom filters."""
        mock_html = """
        <table>
            <tr><th>Term</th><th>Description</th><th>Declared in document(s)</th></tr>
            <tr>
                <td>Test</td>
                <td>Test definition</td>
                <td><table></table></td>
            </tr>
        </table>
        """

        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.text = mock_html
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response

        client = TeddiClient(client=mock_client)
        request = SearchRequest(
            term="test",
            search_in=SearchIn.DEFINITIONS,
            search_pattern=SearchPattern.STARTING_WITH,
            technical_bodies=["STQ"],
        )
        await client.search_terms(request)

        # Verify HTTP call was made with correct parameters
        mock_client.post.assert_called_once()
        call_args, call_kwargs = mock_client.post.call_args
        assert call_kwargs["data"]["qWhatToSearch"] == "test"
        assert call_kwargs["data"]["qWhatOption"] == 2  # DEFINITIONS
        assert call_kwargs["data"]["qWhereOption"] == 3  # STARTING_WITH
        assert call_kwargs["data"]["qShowTBs"] == "STQ"
        assert call_kwargs["data"]["btnSearch.x"] == 0
        assert call_kwargs["data"]["btnSearch.y"] == 0

    async def test_search_with_multiple_technical_bodies(self) -> None:
        """Test search with multiple technical bodies keeps TEDDI casing."""
        mock_html = """
        <table>
            <tr><th>Term</th><th>Description</th><th>Declared in document(s)</th></tr>
        </table>
        """

        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.text = mock_html
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response

        client = TeddiClient(client=mock_client)
        request = SearchRequest(
            term="test",
            technical_bodies=["Ecma", "STQ"],
        )
        await client.search_terms(request)

        call_args, call_kwargs = mock_client.post.call_args
        assert call_kwargs["data"]["qShowTBs"] == "Ecma,STQ"

    async def test_get_available_technical_bodies_parses_menu(self) -> None:
        """Test technical bodies are read from the TEDDI search form."""
        menu_html = """
        <form>
          <select name="qShowTBs">
            <option value="ALL" selected>ALL TBs</option>
            <option value=""></option>
            <option value="3GPP">3GPP</option>
            <option value="Ecma">Ecma</option>
            <option value="STQ">STQ</option>
          </select>
        </form>
        """

        mock_client = AsyncMock()
        mock_response = AsyncMock(text=menu_html)
        mock_response.raise_for_status = Mock()
        mock_client.get.return_value = mock_response

        client = TeddiClient(client=mock_client)
        bodies = await client.get_available_technical_bodies()

        assert bodies == ["3GPP", "Ecma", "STQ"]

    async def test_get_available_technical_bodies_falls_back(self) -> None:
        """Test technical bodies fall back to the bundled list on HTTP errors."""
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.HTTPError("unavailable")

        client = TeddiClient(client=mock_client)
        bodies = await client.get_available_technical_bodies()

        assert "3GPP" in bodies
        assert "ALL" not in bodies

    async def test_search_without_client_raises_error(self) -> None:
        """Test that search without initializing client raises error."""
        client = TeddiClient()
        request = SearchRequest(term="test")

        with pytest.raises(RuntimeError, match="Client not initialized"):
            await client.search_terms(request)

    async def test_context_manager_usage(self) -> None:
        """Test using TeddiClient as async context manager."""
        with patch("src.teddi_tool.client.create_cached_teddi_async_client") as mock_create:
            mock_client = AsyncMock()
            mock_response = AsyncMock(text="<table></table>")
            mock_response.raise_for_status = Mock()
            mock_client.post.return_value = mock_response
            mock_create.return_value = mock_client

            async with TeddiClient() as client:
                request = SearchRequest(term="test")
                response = await client.search_terms(request)
                assert response is not None

            mock_client.aclose.assert_called_once()

    async def test_fetch_document(self) -> None:
        """Test fetching document content."""
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.content = b"PDF content"
        mock_response.raise_for_status = Mock()
        mock_client.get.return_value = mock_response

        client = TeddiClient(client=mock_client)
        content = await client.fetch_document("https://example.com/doc.pdf")

        assert content == b"PDF content"
        mock_client.get.assert_called_once_with("https://example.com/doc.pdf")
