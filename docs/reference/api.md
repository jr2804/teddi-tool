# API Reference

The package exposes its public surface from `teddi_tool`:

```python
from teddi_tool import SearchIn, TechnicalBody, TeddiClient
```

## Models (`teddi_tool.models`)

### Enums

| Enum | Values |
|------|--------|
| `SearchIn` | `both`, `terms`, `definitions`, `abbreviations` |
| `SearchPattern` | `all-occurrences`, `exactmatch`, `startingwith` |
| `TechnicalBody` | `all` (single value; TEDDI exposes no per-TB list) |
| `OutputFormat` | `table`, `json`, `ison`, `toon` |

### Dataclasses

- `SearchRequest(term, *, search_in=SearchIn.BOTH, search_pattern=SearchPattern.ALL_OCCURRENCES,
  technical_bodies=None)` — one query; `technical_bodies` is a list of `TechnicalBody` or `None`.
- `SearchResponse(results: list[TermResult], query: SearchRequest)` — parsed response.
- `TermResult(term, definition, abbreviation, technical_body, source, documents)` — one row of the TEDDI results table.
- `DocumentRef(title, url, reference)` — a document linked from a term row.

## Client (`teddi_tool.client`)

### `TeddiSource` (Protocol)

The seam consumers should type against:

```python
class TeddiSource(Protocol):
    async def search_terms(self, request: SearchRequest) -> SearchResponse: ...
    async def get_available_technical_bodies(self) -> list[TechnicalBody]: ...
    async def fetch_document(self, url: str) -> bytes: ...
```

### `TeddiClient`

Async context manager. `POST https://webapp.etsi.org/Teddi/Main.asp` with form
fields `qWhatToSearch`, `qWhereOption`, `qWhatOption`, `qShowTBs`,
`btnSearch.x`, `btnSearch.y`.

```python
async with TeddiClient() as client:
    response = await client.search_terms(SearchRequest(term="QoS"))
for result in response.results:
    print(result.term)
```

- `TeddiClient(client: httpx.AsyncClient | None = None)` — inject a client to bypass
  the cache; otherwise one is created on `__aenter__` and closed on `__aexit__`.
- `search_terms(request)` → `SearchResponse`; raises `ValueError` if the response
  cannot be parsed and `httpx.HTTPError` on transport failures.
- `get_available_technical_bodies()` — static enum values (excluding `ALL`).
- `fetch_document(url)` → `bytes` — not exposed as a CLI command or MCP tool.

### Cached HTTP client (`teddi_tool.http_client`)

`create_cached_teddi_async_client(cache_dir: Path | None = None, cache_ttl: int = 7200)`
returns an `httpx.AsyncClient` backed by hishel's `AsyncSqliteStorage` at
`.cache/teddi_http.sqlite3` (or `cache_dir / "teddi_http.sqlite3"`). TTL is fixed at
write time; there is no refresh-on-access. Timeout is 30 s and a browser
User-Agent is sent.

## Parser (`teddi_tool.parser`)

`parse_teddi_response(html: str) -> list[TermResult]` parses the nested results
tables. Empty technical-body cells inherit the previous row's TB; document
sub-tables become `DocumentRef` entries. Local links are resolved to absolute
TEDDI URLs.

## Output helpers (`teddi_tool.search_utils`)

- `execute_search(term, scope, pattern, technical_bodies)` — parse filters, query,
  and return a `SearchResponse`.
- `execute_list_bodies()` — list supported technical bodies.
- `build_results_payload(...)` / `serialize_payload(payload, format)` — structure
  and render results as JSON, ISON, or TOON.
- `render_table(response)` — rich table for the CLI.
- `parse_technical_bodies(value)` — parse a comma-separated TB filter.

## MCP server (`teddi_tool.server`)

Tools: `search_teddi`, `get_term_info`, `list_technical_bodies`. Run with
`teddi-mcp` or `teddi server`.
