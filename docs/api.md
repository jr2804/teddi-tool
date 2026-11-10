# API Reference

## Enums

### `OutputFormat`

Output format for CLI results.

```python
class OutputFormat(StrEnum):
    JSON = "json"
    ISON = "ison"
    TOON = "toon"
    TABLE = "table"
```

### `SearchIn`

Search scope: where to search for the term.

```python
class SearchIn(StrEnum):
    ABBREVIATIONS = "abbreviations"
    DEFINITIONS = "definitions"
    BOTH = "both"
```

### `SearchPattern`

Search pattern: how to match the term.

```python
class SearchPattern(StrEnum):
    ALL_OCCURRENCES = "alloccurrences"
    EXACT_MATCH = "exactmatch"
    STARTING_WITH = "startingwith"
    ENDING_WITH = "endingwith"
```

### `TechnicalBody`

ETSI and standardization body identifiers.

```python
class TechnicalBody(StrEnum):
    ALL = "all"
```

## Data Classes

### `DocumentRef`

Reference to a specification document from TEDDI results.

```python
@dataclass
class DocumentRef:
    technical_body: str      # e.g., '3GPP'
    specification: str       # e.g., 'TS 24.008'
    url: str                # Full HTTP URL to the specification
```

### `TermResult`

A single term found in TEDDI with its definition and document references.

```python
@dataclass
class TermResult:
    term: str                              # The term/abbreviation found
    description: str                        # Definition or description
    documents: list[DocumentRef]           # Documents grouped by technical body
```

### `SearchRequest`

Request parameters for TEDDI search.

```python
@dataclass
class SearchRequest:
    term: str                                           # Term to search for
    search_in: SearchIn = SearchIn.BOTH                 # Scope
    search_pattern: SearchPattern = SearchPattern.ALL_OCCURRENCES  # Pattern
    technical_bodies: list[TechnicalBody] | None = None  # Filter by TBs
```

### `SearchResponse`

Response from TEDDI search containing all matching terms.

```python
@dataclass
class SearchResponse:
    query: SearchRequest        # Original search request
    results: list[TermResult]   # Terms found matching the criteria
    total_count: int           # Total number of matching results
```

## Client

### `TeddiClient`

Main client for TEDDI search operations.

```python
class TeddiClient:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        """Initialize client with optional custom HTTP client."""

    async def __aenter__(self) -> "TeddiClient":
        """Async context manager entry."""

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit."""

    async def search_terms(self, request: SearchRequest) -> SearchResponse:
        """Search for terms in TEDDI."""

    async def get_available_technical_bodies(self) -> list[str]:
        """Get list of available technical bodies."""

    async def fetch_document(self, url: str) -> bytes:
        """Fetch document content from URL."""
```

## HTTP Client

### `create_cached_teddi_async_client`

Creates an async HTTP client with caching.

```python
def create_cached_teddi_async_client(
    cache_dir: Path | None = None,
    cache_ttl: int = 7200,
) -> httpx.AsyncClient:
    """
    Create async HTTP client with hishel caching.

    - SQLite cache in `.cache/teddi_http.sqlite3`
    - TTL: 2 hours (7200 seconds) by default, fixed at write time
    - No retry transport; HTTP failures surface as `httpx.HTTPError`
    """
```

## Parser

### `parse_teddi_response`

Parse TEDDI HTML response into structured results.

```python
def parse_teddi_response(html: str) -> list[TermResult]:
    """
    Parse HTML table response from TEDDI search.
    
    Handles:
    - Nested tables for document references
    - TB grouping (empty cells inherit from previous)
    - Relative URL resolution
    """
```

## TEDDI Endpoint

**POST** `https://webapp.etsi.org/Teddi/search`

**Parameters:**

- `qWhatToSearch`: Term to search
- `qWhereOption`: Search scope (1=abbreviations, 3=definitions, 2=both)
- `qWhatOption`: Match pattern (1=alloccurrences, 2=startingwith, 3=endingwith, 4=exactmatch)
- `qShowTBs`: Technical body filter (default: all)
- `btnSearch.x`, `btnSearch.y`: Search button coordinates

**Response:** HTML table parsed by `parse_teddi_response()`
