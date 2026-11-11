"""Dataclasses and enums for TEDDI search integration."""

from dataclasses import dataclass
from enum import StrEnum

# Technical-body codes offered by the TEDDI search form (``select[name=qShowTBs]``
# in https://webapp.etsi.org/Teddi/Menu.asp). Values are case-sensitive on the
# server side, so they are stored exactly as TEDDI publishes them.
TECHNICAL_BODY_CODES: tuple[str, ...] = (
    "3GPP",
    "AERO",
    "AFI",
    "ARF",
    "AT",
    "ATA",
    "ATM",
    "ATTM",
    "BOARD",
    "BRAN",
    "BROADCAS",
    "BT",
    "BTC",
    "CABLE",
    "CCM",
    "CDM",
    "CIM",
    "CLOUD",
    "CN",
    "CYBER",
    "DATA",
    "DECT",
    "DTA",
    "E2NA",
    "E4P",
    "EASI",
    "ECI",
    "Ecma",
    "ECMATC32",
    "EE",
    "eHEALTH",
    "EMTEL",
    "ENI",
    "ERM",
    "ESI",
    "ETI",
    "F5G",
    "GA",
    "GRID",
    "HF",
    "ICC",
    "IMCC",
    "INS",
    "INT",
    "IP6",
    "IPE",
    "IPRC",
    "ISAC",
    "ISI",
    "ISM",
    "ITS",
    "LI",
    "LIS",
    "LTN",
    "M2M",
    "MAT",
    "MBC",
    "MCD",
    "M-COMM",
    "MEC",
    "MESA",
    "MMG",
    "MOI",
    "MSG",
    "MTA",
    "MTC",
    "MTS",
    "mWT",
    "NA",
    "NFV",
    "NGP",
    "NIN",
    "NTECH",
    "OCG",
    "OEU",
    "oneM2M",
    "ORI",
    "OSG",
    "OSM",
    "PDL",
    "PLT",
    "PS",
    "PTS",
    "QKD",
    "QSC",
    "RES",
    "RIS",
    "RRS",
    "RT",
    "SAFETY",
    "SAGE",
    "SAI",
    "SCP",
    "SEC",
    "SES",
    "SET",
    "SmartBAN",
    "SmartM2M",
    "SMG",
    "SMT",
    "SPAN",
    "SPS",
    "STQ",
    "TCCE",
    "TE",
    "TETRA",
    "THz",
    "TIPHON",
    "TISPAN",
    "TM",
    "TMN",
    "TRAC",
    "UMTS",
    "USER",
    "ZSM",
)


class OutputFormat(StrEnum):
    """Output format for CLI results."""

    JSON = "json"
    ISON = "ison"
    TOON = "toon"
    TABLE = "table"


class SearchIn(StrEnum):
    """Search scope: where to search for the term."""

    ABBREVIATIONS = "abbreviations"
    DEFINITIONS = "definitions"
    BOTH = "both"


class SearchPattern(StrEnum):
    """Search pattern: how to match the term."""

    ALL_OCCURRENCES = "alloccurrences"
    EXACT_MATCH = "exactmatch"
    STARTING_WITH = "startingwith"
    ENDING_WITH = "endingwith"


@dataclass
class DocumentRef:
    """Reference to a specification document from TEDDI results."""

    technical_body: str
    """Technical body that published this specification (e.g., '3GPP')."""

    specification: str
    """Specification identifier (e.g., 'TS 24.008')."""

    url: str
    """Full HTTP URL to the specification."""


@dataclass
class TermResult:
    """A single term found in TEDDI with its definition and document references."""

    term: str
    """The term/abbreviation found."""

    description: str
    """Definition or description of the term."""

    documents: list[DocumentRef]
    """List of documents where this term is declared, grouped by technical body."""


@dataclass
class SearchRequest:
    """Request parameters for TEDDI search."""

    term: str
    """Term to search for."""

    search_in: SearchIn = SearchIn.BOTH
    """Scope: search in abbreviations, definitions, or both."""

    search_pattern: SearchPattern = SearchPattern.ALL_OCCURRENCES
    """Pattern: exact match, starts with, etc."""

    technical_bodies: list[str] | None = None
    """Filter by technical bodies. None or empty = all TBs."""


@dataclass
class SearchResponse:
    """Response from TEDDI search containing all matching terms."""

    query: SearchRequest
    """Original search request."""

    results: list[TermResult]
    """List of terms found matching the search criteria."""

    total_count: int
    """Total number of matching results."""
