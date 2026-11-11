"""TEDDI Tool: CLI and FastMCP server for ETSI TEDDI search."""

from teddi_tool.__about__ import __version__
from teddi_tool.client import TeddiClient, TeddiSource
from teddi_tool.models import (
    DocumentRef,
    OutputFormat,
    SearchIn,
    SearchPattern,
    SearchRequest,
    SearchResponse,
    TechnicalBody,
    TermResult,
)

__all__ = [
    "DocumentRef",
    "OutputFormat",
    "SearchIn",
    "SearchPattern",
    "SearchRequest",
    "SearchResponse",
    "TechnicalBody",
    "TeddiClient",
    "TeddiSource",
    "TermResult",
    "__version__",
]
