"""TEDDI Tool: CLI and FastMCP server for ETSI TEDDI search."""

from teddi_tool.__about__ import __version__
from teddi_tool.client import TeddiClient, TeddiSource
from teddi_tool.models import (
    TECHNICAL_BODY_CODES,
    DocumentRef,
    OutputFormat,
    SearchIn,
    SearchPattern,
    SearchRequest,
    SearchResponse,
    TermResult,
)

__all__ = [
    "TECHNICAL_BODY_CODES",
    "DocumentRef",
    "OutputFormat",
    "SearchIn",
    "SearchPattern",
    "SearchRequest",
    "SearchResponse",
    "TeddiClient",
    "TeddiSource",
    "TermResult",
    "__version__",
]
