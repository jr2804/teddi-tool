"""HTML parser for TEDDI search results and search-form metadata."""

import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from teddi_tool.models import DocumentRef, TermResult

TEDDI_BASE_URL = "https://webapp.etsi.org"

_EXTERNAL_URL_PREFIXES = ("http://", "https://", "//")

_ALL_TECHNICAL_BODIES = "ALL"

logger = logging.getLogger(__name__)


def parse_technical_bodies_page(html_content: str) -> list[str]:
    """Parse technical-body codes from the TEDDI search form.

    Args:
        html_content: HTML of the TEDDI menu page containing the ``qShowTBs``
            select element.

    Returns:
        Technical-body codes in menu order, excluding the ``ALL`` sentinel and
        empty entries.

    Raises:
        ValueError: If the page does not contain a ``qShowTBs`` select element.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    select = soup.find("select", attrs={"name": "qShowTBs"})
    if select is None:
        message = "TEDDI menu page does not contain a qShowTBs select element"
        raise ValueError(message)

    bodies: list[str] = []
    for option in select.find_all("option"):
        value = option.get("value")
        if not isinstance(value, str):
            continue
        code = value.strip()
        if not code or code == _ALL_TECHNICAL_BODIES or code in bodies:
            continue
        bodies.append(code)

    return bodies


def parse_teddi_response(html_content: str) -> list[TermResult]:
    """Parse TEDDI HTML response to extract search results.

    Extracts term, definition, and document references with TB grouping logic.

    Args:
        html_content: Raw HTML response from TEDDI search endpoint.

    Returns:
        List of TermResult objects parsed from HTML; empty when the page has no
        results table.
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

        term_cell = _clean_text(cells[0])
        description_cell = _clean_text(cells[1])

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
        tb_cell = _clean_text(cells[0])
        if tb_cell:
            last_tb = tb_cell

        # Second cell may contain one or more document links
        links = cells[1].find_all("a")
        if not links:
            # No link in this row, skip
            continue

        for link in links:
            spec_text = _clean_text(link)
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


def _clean_text(element: Tag) -> str:
    """Return element text with tag boundaries and whitespace normalised.

    ``<br>`` separators and adjacent inline tags are rendered as a single
    space, so words from different nodes never run together.

    Args:
        element: Cell or anchor element to read.

    Returns:
        Whitespace-normalised text content.
    """
    return " ".join(element.get_text(" ", strip=True).split())


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
