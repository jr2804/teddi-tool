"""Tests for Pydantic models and enums."""

from src.teddi_tool.models import (
    TECHNICAL_BODY_CODES,
    DocumentRef,
    OutputFormat,
    SearchIn,
    SearchPattern,
    SearchRequest,
    SearchResponse,
    TermResult,
)


class TestEnums:
    """Test enum definitions and values."""

    def test_search_in_enum_values(self) -> None:
        """Test SearchIn enum has expected values."""
        assert SearchIn.ABBREVIATIONS.value == "abbreviations"
        assert SearchIn.DEFINITIONS.value == "definitions"
        assert SearchIn.BOTH.value == "both"

    def test_search_pattern_enum_values(self) -> None:
        """Test SearchPattern enum has expected values."""
        assert SearchPattern.ALL_OCCURRENCES.value == "alloccurrences"
        assert SearchPattern.EXACT_MATCH.value == "exactmatch"
        assert SearchPattern.STARTING_WITH.value == "startingwith"
        assert SearchPattern.ENDING_WITH.value == "endingwith"

    def test_technical_body_codes_are_usable(self) -> None:
        """Test the bundled technical-body codes mirror the TEDDI menu."""
        assert len(TECHNICAL_BODY_CODES) > 100
        assert "3GPP" in TECHNICAL_BODY_CODES
        assert "STQ" in TECHNICAL_BODY_CODES
        assert "Ecma" in TECHNICAL_BODY_CODES
        assert "ALL" not in TECHNICAL_BODY_CODES
        assert all(code.strip() for code in TECHNICAL_BODY_CODES)
        assert len(set(TECHNICAL_BODY_CODES)) == len(TECHNICAL_BODY_CODES)

    def test_output_format_enum_values(self) -> None:
        """Test OutputFormat enum has expected values."""
        assert OutputFormat.TABLE.value == "table"
        assert OutputFormat.JSON.value == "json"
        assert OutputFormat.ISON.value == "ison"
        assert OutputFormat.TOON.value == "toon"


class TestDataClasses:
    """Test dataclass definitions and instantiation."""

    def test_document_ref_creation(self) -> None:
        """Test DocumentRef creation with all fields."""
        doc = DocumentRef(
            technical_body="3GPP",
            specification="TS 24.008",
            url="https://example.com/ts-24-008",
        )
        assert doc.technical_body == "3GPP"
        assert doc.specification == "TS 24.008"
        assert doc.url == "https://example.com/ts-24-008"

    def test_term_result_creation(self) -> None:
        """Test TermResult creation with documents."""
        doc = DocumentRef(
            technical_body="3GPP",
            specification="TS 24.008",
            url="https://example.com/ts",
        )
        result = TermResult(
            term="QoS",
            description="Quality of Service",
            documents=[doc],
        )
        assert result.term == "QoS"
        assert result.description == "Quality of Service"
        assert len(result.documents) == 1
        assert result.documents[0].technical_body == "3GPP"

    def test_search_request_defaults(self) -> None:
        """Test SearchRequest has correct default values."""
        request = SearchRequest(term="test")
        assert request.term == "test"
        assert request.search_in == SearchIn.BOTH
        assert request.search_pattern == SearchPattern.ALL_OCCURRENCES
        assert request.technical_bodies is None

    def test_search_request_with_filters(self) -> None:
        """Test SearchRequest with custom filters."""
        request = SearchRequest(
            term="QoS",
            search_in=SearchIn.DEFINITIONS,
            search_pattern=SearchPattern.STARTING_WITH,
            technical_bodies=["3GPP", "STQ"],
        )
        assert request.term == "QoS"
        assert request.search_in == SearchIn.DEFINITIONS
        assert request.search_pattern == SearchPattern.STARTING_WITH
        assert request.technical_bodies == ["3GPP", "STQ"]

    def test_search_response_creation(self) -> None:
        """Test SearchResponse creation with results."""
        request = SearchRequest(term="test")
        doc = DocumentRef(
            technical_body="3GPP",
            specification="TS 24.008",
            url="https://example.com/ts",
        )
        result = TermResult(
            term="QoS",
            description="Quality of Service",
            documents=[doc],
        )
        response = SearchResponse(
            query=request,
            results=[result],
            total_count=1,
        )
        assert response.query == request
        assert len(response.results) == 1
        assert response.total_count == 1
