"""HTML parser for TEDDI search results."""

import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from teddi_tool.models import DocumentRef, TermResult

logger = logging.getLogger(__name__)

TEDDI_BASE_URL = "https://webapp.etsi.org"

_EXTERNAL_URL_PREFIXES = ("http://", "https://", "//")


def parse_teddi_response(html_content: str) -> list[TermResult]:
    """Parse TEDDI HTML response to extract search results.

    Extracts term, definition, and document references with TB grouping logic.

    Args:
        html_content: Raw HTML response from TEDDI search endpoint.

    Returns:
        List of TermResult objects parsed from HTML.

    Raises:
        ValueError: If HTML structure cannot be parsed.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    results_table = _find_results_table(soup)
    if results_table is None:
        return []

    return _extract_results(results_table)


def _find_results_table(soup: BeautifulSoup) -> Tag | None:
    """Locate the results table in a parsed TEDDI page.

    Prefers the table whose first column header contains "term"; falls back to
    the first table with more than a few rows (layout tables are small).

    Args:
        soup: Parsed TEDDI response document.

    Returns:
        The results table, or None when the page contains no usable table.
    """
    tables = soup.find_all("table")
    if not tables:
        logger.warning("No tables found in TEDDI response HTML")
        return None

    # Search all tables for one with a header row containing "Term"
    for table in tables:
        for row in table.find_all("tr"):
            cells = row.find_all(["th", "td"])
            if len(cells) < 3:
                continue
            if "term" in cells[0].get_text(strip=True).lower():
                return table

    # Fall back to the first table that looks like content rather than layout
    for table in tables:
        if len(table.find_all("tr")) > 5:
            return table

    return None


def _extract_results(table: Tag) -> list[TermResult]:
    """Extract one TermResult per data row of the results table.

    Args:
        table: Results table found by `_find_results_table`.

    Returns:
        Term results in document order; the header row is skipped.
    """
    results: list[TermResult] = []

    for row in table.find_all("tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) < 3:
            continue

        term_cell = cells[0].get_text(strip=True)
        description_cell = cells[1].get_text(strip=True)

        # Skip the header row if it was included
        if term_cell.lower() == "term" and description_cell.lower() == "description":
            continue

        if not term_cell or not description_cell:
            continue

        # Third column may contain a nested table of document references
        results.append(
            TermResult(
                term=term_cell,
                description=description_cell,
                documents=_parse_document_table(cells[2]),
            )
        )

    return results


def _parse_document_table(cell_content: Tag) -> list[DocumentRef]:
    """Parse nested table in 'Declared in document(s)' cell with TB grouping.

    Handles TB grouping: if TB column is empty, inherit from previous row.
    Each row of the nested table has 2 columns: [TB] [Document link]

    Args:
        cell_content: BeautifulSoup cell element containing nested table.

    Returns:
        List of DocumentRef objects with TB grouping applied.
    """
    documents: list[DocumentRef] = []
    nested_table = cell_content.find("table")

    if not nested_table:
        # No nested table, return empty
        return documents

    last_tb = ""  # Track last seen technical body for grouping

    for row in nested_table.find_all("tr"):
        cells = row.find_all(["td", "th"])

        if len(cells) < 2:
            # Skip rows with less than 2 cells
            continue

        # First cell may contain TB name or be empty
        tb_cell = cells[0].get_text(strip=True)
        if tb_cell:
            last_tb = tb_cell

        # Second cell contains link or is empty
        link = cells[1].find("a")
        if not link:
            # No link in this row, skip
            continue

        spec_text = link.get_text(strip=True)
        if not spec_text:
            continue

        documents.append(
            DocumentRef(
                technical_body=last_tb,
                specification=spec_text,
                url=_resolve_url(link),
            )
        )

    return documents


def _resolve_url(link: Tag) -> str:
    """Return the absolute document URL for a link element.

    Args:
        link: Anchor element from a document sub-table.

    Returns:
        Absolute URL, or an empty string when the anchor has no href.
    """
    href = link.get("href")
    url = href if isinstance(href, str) else ""

    # Resolve relative URLs against the TEDDI host
    if url and not url.startswith(_EXTERNAL_URL_PREFIXES):
        return urljoin(TEDDI_BASE_URL, url)

    return url
