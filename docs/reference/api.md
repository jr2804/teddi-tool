# API Reference

The package exposes its public surface from `teddi_tool`:

```python
from teddi_tool import SearchIn, SearchPattern, TeddiClient
```

## Models (`teddi_tool.models`)

### Enums

| Enum | Values |
|------|--------|
| `SearchIn` | `abbreviations`, `definitions`, `both` |
| `SearchPattern` | `alloccurrences`, `exactmatch`, `startingwith`, `endingwith` |
| `OutputFormat` | `table`, `json`, `ison`, `toon` |

Technical-body codes are not bundled: the live list is fetched from the TEDDI
menu page (`https://webapp.etsi.org/Teddi/Menu.asp`) through a client whose
hishel cache uses a 90-day TTL. Filter parsing accepts codes
case-insensitively against that list and also accepts `all`.

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

- `TeddiClient(client: httpx2.AsyncClient | None = None, cache_dir: Path | None = None,`
  `cache_ttl: int = SEARCH_CACHE_TTL, menu_cache_ttl: int = TEDDI_MENU_CACHE_TTL)`
  — inject a client to bypass the cache; otherwise two cached clients (search:
  `cache_ttl`, default 2 h; menu: `menu_cache_ttl`, default 90 days) are created
  on `__aenter__` and closed on `__aexit__` (using `cache_dir` when given).
  Non-positive TTLs raise `ValueError`.
- `search_terms(request)` → `SearchResponse`; raises `ValueError` if the
  response cannot be parsed and `httpx2.HTTPError` on transport failures.
- `get_available_technical_bodies()` → `list[str]`; reads
  `https://webapp.etsi.org/Teddi/Menu.asp` through a client cached for 90 days
  (`TEDDI_MENU_CACHE_TTL`). There is no fallback list: HTTP or parse errors
  propagate.
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
  TEDDI URLs. Returns an empty list when the page has no results table.
- `parse_technical_bodies_page(html) -> list[str]` reads
  `select[name=qShowTBs]`, dropping the `ALL` sentinel and empty options; raises
  `ValueError` when the select is missing.

## Output helpers (`teddi_tool.search_utils`)

- `execute_search(term, search_scope, search_pattern, tb_filter_str, *,`
  `cache_ttl=SEARCH_CACHE_TTL, menu_cache_ttl=TEDDI_MENU_CACHE_TTL)` — parse
  filters, query TEDDI, and return the `(SearchRequest, SearchResponse)` pair.
- `execute_list_bodies(menu_cache_ttl=TEDDI_MENU_CACHE_TTL)` → `list[str]` —
  technical bodies for `list-bodies`.
- `build_results_payload(request, response)` / `serialize_payload(payload,
  format)` — structure and render results as JSON, ISON, or TOON.
- `render_table(term, response)` — rich table for the CLI.
- `parse_technical_bodies(value, known_bodies)` - normalise a comma-separated
  filter against `known_bodies` (the codes TEDDI currently advertises, from the
  90-day-cached menu list). `all` becomes `["ALL"]`; unknown codes raise
  `ValueError` listing the supported values.

### Result payload

`build_results_payload()` returns the structure used by JSON, ISON, TOON and the
MCP tools:

```json
{
  "query": {
    "term": "QoS",
    "search_in": "both",
    "search_pattern": "exactmatch",
    "technical_bodies": ["STQ"]
  },
  "total_count": 2,
  "results": [
    {
      "term": "QoS",
      "description": "Quality of Service",
      "documents": [
        {"technical_body": "STQ", "specification": "TS 102 894-2", "url": "https://..."}
      ]
    }
  ]
}
```

## MCP server (`teddi_tool.server`)

Tools: `search_teddi`, `get_term_info`, `list_technical_bodies`. Run with
`teddi-mcp` or `teddi-tool server`.
