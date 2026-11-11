"""Tests for shared search helpers."""

import pytest

from src.teddi_tool.models import TECHNICAL_BODY_CODES, SearchRequest, SearchResponse
from src.teddi_tool.search_utils import build_results_payload, parse_technical_bodies


class TestParseTechnicalBodies:
    """Test parsing and normalisation of technical-body filters."""

    def test_empty_filter_returns_none(self) -> None:
        """Test empty and blank filters are treated as no filter."""
        assert parse_technical_bodies(None) is None
        assert parse_technical_bodies("") is None
        assert parse_technical_bodies(" , ") is None

    def test_codes_are_case_insensitive(self) -> None:
        """Test input is normalised to the casing TEDDI publishes."""
        assert parse_technical_bodies("3gpp, stq") == ["3GPP", "STQ"]
        assert parse_technical_bodies("ecma") == ["Ecma"]
        assert parse_technical_bodies("EHEALTH") == ["eHEALTH"]

    def test_all_maps_to_sentinel(self) -> None:
        """Test the 'all' filter maps to the TEDDI ALL sentinel."""
        assert parse_technical_bodies("all") == ["ALL"]

    def test_unknown_code_raises_with_supported_values(self) -> None:
        """Test unknown codes are rejected with an actionable message."""
        with pytest.raises(ValueError, match="Invalid technical body 'XYZ'") as exc_info:
            parse_technical_bodies("XYZ")

        assert TECHNICAL_BODY_CODES[0] in str(exc_info.value)
        assert "ALL" in str(exc_info.value)


class TestBuildResultsPayload:
    """Test the canonical machine-readable payload."""

    def test_payload_contains_canonical_filter_values(self) -> None:
        """Test technical bodies are emitted as plain strings."""
        request = SearchRequest(term="QoS", technical_bodies=["3GPP", "STQ"])
        response = SearchResponse(query=request, results=[], total_count=0)

        payload = build_results_payload(request, response)

        assert payload["query"]["technical_bodies"] == ["3GPP", "STQ"]
        assert payload["total_count"] == 0
