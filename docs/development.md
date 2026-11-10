# Development Guide

## Setup

1. Clone the repository:

   ```bash
   git clone https://forge.3gpp.org/rep/reimes/teddi-mcp.git
   cd teddi-mcp
   ```

2. Sync dependencies (Python 3.13+, `uv`):

   ```bash
   uv sync --all-extras
   ```

Development tools are pinned in `.config/mise/config.toml`; `mise install`
sets up `uv`, `node`, `bun`, and the quality tools.

## Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=teddi_mcp --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_parser.py -v
```

Tests never call TEDDI: they mock the `httpx` client (see
`tests/test_client.py`).

## Code Quality

```bash
# Format (undersort + ruff import sort + ruff format)
mise run format

# Lint
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/

# Type checking
uv run ty check

# Secrets/quality scan
mise run analyze
```

## Project Layout

The package lives in `src/teddi_mcp/`; module-level contracts are documented
in [`src/teddi_mcp/AGENTS.md`](../src/teddi_mcp/AGENTS.md) and test
conventions in [`tests/AGENTS.md`](../tests/AGENTS.md). For a current file
list, run `rg --files` instead of relying on a checked-in tree.

Module overview:

- `models.py` — Pydantic models and enums
- `client.py` — `TeddiSource` protocol and `TeddiClient`
- `parser.py` — TEDDI HTML parsing with TB grouping
- `http_client.py` — hishel-cached async HTTP client
- `search_utils.py` — shared search execution and output rendering
- `cli.py`, `search_cli.py` — Typer entry points
- `server.py` — FastMCP 3.0 server

## Key Design Patterns

### Protocol-Based Abstraction

`TeddiSource` (`src/teddi_mcp/client.py`) is the seam between consumers and
TEDDI, which keeps the client mockable:

```python
class TeddiSource(Protocol):
    async def search_terms(self, request: SearchRequest) -> SearchResponse: ...
    async def get_available_technical_bodies(self) -> list[TechnicalBody]: ...
    async def fetch_document(self, url: str) -> bytes: ...
```

`TeddiClient` implements it and must be used as an async context manager.

### HTTP Caching

Requests go through `create_cached_teddi_async_client()`:

- SQLite store: `.cache/teddi_http.sqlite3` (or the given `cache_dir`)
- TTL: 2 hours, fixed when the entry is written
- 30 s timeout, browser User-Agent

There is no retry transport; failed requests surface as `httpx.HTTPError`.

### TB Grouping in Parser

TEDDI results use nested tables. The parser handles TB inheritance:

- Empty TB cell inherits the previous row's technical body
- Document sub-tables become `DocumentRef` entries

### Dual API: MCP + CLI

MCP tools and CLIs share the same execution path:

- `search_teddi` / `search-term` / `term` — search with filters
- `list_technical_bodies` / `list-bodies` — list technical bodies

`fetch_document()` exists on the client but is not exposed as a tool or
command.

## Adding Features

### New Search Filter

1. Define/extend the enum in `src/teddi_mcp/models.py`
2. Add the field to `SearchRequest`
3. Map it to a TEDDI form field in `src/teddi_mcp/client.py`
4. Expose it in `src/teddi_mcp/cli.py` and `src/teddi_mcp/search_cli.py`
5. Expose it in the MCP tool in `src/teddi_mcp/server.py`
6. Add tests

## Implementation Notes

1. **TEDDI HTML-driven**: the search form was reverse-engineered; the parser
   may need updates if the TEDDI UI changes.
2. **Async-first**: all client methods are `async`; Typer commands wrap them
   with `asyncio.run()`.
3. **Offline tests**: cache paths in tests are temporary (`cache_dir`
   fixture), never the repository `.cache/`.
