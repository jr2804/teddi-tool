"""Tests for HTML parsing of TEDDI responses."""

import pytest

from src.teddi_tool.parser import parse_technical_bodies_page, parse_teddi_response


class TestParseTermResult:
    """Test parsing of term results from HTML."""

    def test_parse_simple_result(self) -> None:
        """Test parsing a simple term result."""
        html = """
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
        results = parse_teddi_response(html)

        assert len(results) == 1
        assert results[0].term == "QoS"
        assert results[0].description == "Quality of Service"
        assert len(results[0].documents) == 1
        assert results[0].documents[0].technical_body == "3GPP"
        assert results[0].documents[0].specification == "TS 24.008"

    def test_parse_result_with_tb_grouping(self) -> None:
        """Test TB grouping: empty TB cells inherit from previous."""
        html = """
        <table>
            <tr><th>Term</th><th>Description</th><th>Declared in document(s)</th></tr>
            <tr>
                <td>Test</td>
                <td>Test definition</td>
                <td>
                    <table>
                        <tr><td>3GPP</td><td></td></tr>
                        <tr><td></td><td><a href="/specs/ts-1">TS 1</a></td></tr>
                        <tr><td></td><td><a href="/specs/ts-2">TS 2</a></td></tr>
                        <tr><td>ETSI</td><td></td></tr>
                        <tr><td></td><td><a href="/specs/es-3">ES 3</a></td></tr>
                    </table>
                </td>
            </tr>
        </table>
        """
        results = parse_teddi_response(html)

        assert len(results) == 1
        result = results[0]
        assert len(result.documents) == 3

        # First two should be grouped under 3GPP
        assert result.documents[0].technical_body == "3GPP"
        assert result.documents[0].specification == "TS 1"
        assert result.documents[1].technical_body == "3GPP"
        assert result.documents[1].specification == "TS 2"

        # Third should be grouped under ETSI
        assert result.documents[2].technical_body == "ETSI"
        assert result.documents[2].specification == "ES 3"

    def test_parse_result_ignores_empty_rows(self) -> None:
        """Test that empty document rows are ignored."""
        html = """
        <table>
            <tr><th>Term</th><th>Description</th><th>Declared in document(s)</th></tr>
            <tr>
                <td>Test</td>
                <td>Test definition</td>
                <td>
                    <table>
                        <tr><td>3GPP</td><td></td></tr>
                        <tr><td></td><td></td></tr>
                        <tr><td></td><td><a href="/specs/ts-1">TS 1</a></td></tr>
                    </table>
                </td>
            </tr>
        </table>
        """
        results = parse_teddi_response(html)

        assert len(results) == 1
        assert len(results[0].documents) == 1
        assert results[0].documents[0].specification == "TS 1"

    def test_parse_multiple_results(self) -> None:
        """Test parsing multiple term results."""
        html = """
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
            <tr>
                <td>PDN</td>
                <td>Packet Data Network</td>
                <td>
                    <table>
                        <tr><td>3GPP</td><td><a href="/specs/ts-23-060">TS 23.060</a></td></tr>
                    </table>
                </td>
            </tr>
        </table>
        """
        results = parse_teddi_response(html)

        assert len(results) == 2
        assert results[0].term == "QoS"
        assert results[1].term == "PDN"

    def test_parse_handles_missing_table(self) -> None:
        """Test parsing when no results table is present."""
        html = "<html><body>No results</body></html>"
        results = parse_teddi_response(html)

        assert results == []

    def test_parse_resolves_relative_urls(self) -> None:
        """Test that relative URLs are resolved to absolute."""
        html = """
        <table>
            <tr><th>Term</th><th>Description</th><th>Declared in document(s)</th></tr>
            <tr>
                <td>Test</td>
                <td>Test definition</td>
                <td>
                    <table>
                        <tr><td>3GPP</td><td><a href="/specs/ts-24-008">TS 24.008</a></td></tr>
                    </table>
                </td>
            </tr>
        </table>
        """
        results = parse_teddi_response(html)

        assert len(results) == 1
        assert results[0].documents[0].url == "https://webapp.etsi.org/specs/ts-24-008"

    def test_parse_handles_absolute_urls(self) -> None:
        """Test that absolute URLs are not modified."""
        html = """
        <table>
            <tr><th>Term</th><th>Description</th><th>Declared in document(s)</th></tr>
            <tr>
                <td>Test</td>
                <td>Test definition</td>
                <td>
                    <table>
                        <tr>
                            <td>3GPP</td>
                            <td><a href="https://example.com/ts-24-008">TS 24.008</a></td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        """
        results = parse_teddi_response(html)

        assert len(results) == 1
        assert results[0].documents[0].url == "https://example.com/ts-24-008"


class TestParseTechnicalBodiesPage:
    """Test parsing of the TEDDI search-form technical-body list."""

    def test_parse_menu_options(self) -> None:
        """Test ALL and empty entries are dropped while casing is kept."""
        html = """
        <form>
          <select name="qShowTBs" size="6">
            <option value="ALL" selected>ALL TBs</option>
            <option value=""></option>
            <option value="3GPP">3GPP</option>
            <option value="Ecma">Ecma</option>
            <option value="eHEALTH">eHEALTH</option>
            <option value="STQ">STQ</option>
          </select>
        </form>
        """
        bodies = parse_technical_bodies_page(html)

        assert bodies == ["3GPP", "Ecma", "eHEALTH", "STQ"]

    def test_missing_select_raises(self) -> None:
        """Test a page without the TB select is rejected."""
        with pytest.raises(ValueError, match="qShowTBs"):
            parse_technical_bodies_page("<html><body>nope</body></html>")
