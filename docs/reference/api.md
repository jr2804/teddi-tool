# API Reference

The package exposes its public surface from `teddi_tool`:

```python
from teddi_tool import SearchIn, SearchPattern, TeddiClient, TECHNICAL_BODY_CODES
```

## Models (`teddi_tool.models`)

### Enums

| Enum | Values |
|------|--------|
| `SearchIn` | `abbreviations`, `definitions`, `both` |
| `SearchPattern` | `alloccurrences`, `exactmatch`, `startingwith`, `endingwith` |
| `OutputFormat` | `table`, `json`, `ison`, `toon` |

`TECHNICAL_BODY_CODES: tuple[str, ...]` holds the 115 codes advertised by the
TEDDI search form (`3GPP`, `Ecma`, `eHEALTH`, `oneM2M`, `STQ`, …). Filter
parsing accepts them case-insensitively and also accepts `all`.

### Dataclasses

- `DocumentRef(technical_body, specification, url)` — one specification linked
  from a term row.
- `TermResult(term, description, documents)` — one result row with its
  document references grouped by technical body.
- `SearchRequest(term, search_in=SearchIn.BOTH,
  search_pattern=SearchPattern.ALL_OCCURRENCES, technical_bodies=None)` —
  `technical_bodies` is a list of TEDDI codes, `["ALL"]`, or `None` for no
  filter.
- `SearchResponse(query, results, total_count)` — parsed response.

## Client (`teddi_tool.client`)

### `TeddiSource` (Protocol)

The seam consumers should type against:

```python
class TeddiSource(Protocol):
    async def search_terms(self, request: SearchRequest) -> SearchResponse: ...
    async def get_available_technical_bodies(self) -> list[str]: ...
    async def fetch_document(self, url: str) -> bytes: ...
```

### `TeddiClient`

Async context manager. `POST https://webapp.etsi.org/Teddi/Main.asp` with form
fields `qWhatToSearch`, `qWhatOption` (scope), `qWhereOption` (pattern),
`qShowTBs`, `btnSearch.x`, `btnSearch.y`.

| Field | Values |
|-------|--------|
| `qWhatOption` | `1` abbreviations, `2` definitions, `3` both |
| `qWhereOption` | `1` exact match, `2` all occurrences, `3` starting with, `4` ending with |

```python
async with TeddiClient() as client:
    response = await client.search_terms(SearchRequest(term="QoS"))
for result in response.results:
    print(result.term)
```

- `TeddiClient(client: httpx2.AsyncClient | None = None)` — inject a client to
  bypass the cache; otherwise one is created on `__aenter__` and closed on
  `__aexit__`.
- `search_terms(request)` → `SearchResponse`; raises `ValueError` if the
  response cannot be parsed and `httpx2.HTTPError` on transport failures.
- `get_available_technical_bodies()` → `list[str]`; reads
  `https://webapp.etsi.org/Teddi/Menu.asp` and falls back to
  `TECHNICAL_BODY_CODES` when the page cannot be fetched or parsed.
- `fetch_document(url)` → `bytes` — not exposed as a CLI command or MCP tool.

### Cached HTTP client (`teddi_tool.http_client`)

`create_cached_teddi_async_client(cache_dir: Path | None = None, cache_ttl: int = 7200)`
returns an `httpx2.AsyncClient` (hishel's `AsyncCacheClient` for httpx2) backed
by `AsyncSqliteStorage` at `.cache/teddi_http.sqlite3` (or
`cache_dir / "teddi_http.sqlite3"`). TTL is fixed at write time; there is no
refresh-on-access. Timeout is 30 s and a browser User-Agent is sent.

## Parser (`teddi_tool.parser`)

- `parse_teddi_response(html) -> list[TermResult]` parses the nested results
  tables. Empty technical-body cells inherit the previous row's TB; document
  sub-tables become `DocumentRef` entries. Local links are resolved to absolute
  TEDDI URLs.
- `parse_technical_bodies_page(html) -> list[str]` reads
  `select[name=qShowTBs]`, dropping the `ALL` sentinel and empty options; raises
  `ValueError` when the select is missing.

## Output helpers (`teddi_tool.search_utils`)

- `execute_search(term, scope, pattern, technical_bodies)` — parse filters,
  query TEDDI, and return a `SearchResponse`.
- `execute_list_bodies()` → `list[str]` — technical bodies for `list-bodies`.
- `build_results_payload(request, response)` / `serialize_payload(payload,
  format)` — structure and render results as JSON, ISON, or TOON.
- `render_table(response)` — rich table for the CLI.
- `parse_technical_bodies(value)` — normalise a comma-separated filter against
  `TECHNICAL_BODY_CODES`; `all` becomes `["ALL"]`, unknown codes raise
  `ValueError`.

## MCP server (`teddi_tool.server`)

Tools: `search_teddi`, `get_term_info`, `list_technical_bodies`. Run with
`teddi-mcp` or `teddi-tool server`.
