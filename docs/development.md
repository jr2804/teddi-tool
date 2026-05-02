# Development Guide

## Setup

1. Clone the repository:

   ```bash
   git clone https://forge.3gpp.org/rep/reimes/teddi-mcp.git
   cd teddi-mcp
   ```

2. Sync dependencies:

   ```bash
   uv sync --all-extras
   ```

3. Install pre-commit hooks:

   ```bash
   uv run pre-commit install
   ```

## Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src.teddi_mcp --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_parser.py -v
```

## Code Quality

```bash
# Format and lint
uv run ruff format
uv run ruff check --fix

# Type checking
uv run pyright
```

## Project Structure

```
teddi-mcp/
├── src/
│   └── teddi_mcp/     # Main package
│       ├── models.py  # Pydantic models
│       ├── client.py  # TeddiClient with Protocol abstraction
│       ├── parser.py   # HTML parsing with TB grouping
│       ├── http_client.py  # HTTP session with hishel caching
│       ├── cli.py     # Typer CLI
│       └── server.py  # FastMCP 3.0 server
├── tests/             # Test suite
├── docs/              # Documentation
├── pyproject.toml     # Project config
└── README.md          # Overview
```

## Key Design Patterns

### Protocol-Based Abstraction

`TeddiSource` protocol enables mocking/swapping TEDDI sources:

```python
class TeddiSource(Protocol):
    async def search_terms(self, request: SearchRequest) -> SearchResponse: ...
    async def get_available_technical_bodies(self) -> list[TechnicalBody]: ...
    async def fetch_document(self, url: str) -> bytes: ...
```

### HTTP Caching

All requests use `create_cached_teddi_session()`:

- SQLite: `.cache/teddi_http.sqlite3`
- TTL: 2 hours (refresh on access)
- Auto-retries: 429, 500, 502, 503, 504

### TB Grouping in Parser

TEDDI results have nested tables. Parser handles TB inheritance:

- Empty TB cell inherits previous TB value
- Results grouped by technical body

### Dual API: MCP + CLI

Both expose identical tools:

- `search_term()` — query with filters
- `list_technical_bodies()` — list TBs
- `fetch_document()` — retrieve content (MCP-only)

## Adding Features

### New Search Filter

1. Define enum in `models.py`
2. Update `SearchRequest` dataclass
3. Update HTTP call in `client.py`
4. Update CLI in `cli.py`
5. Update MCP server in `server.py`
6. Add tests

## Implementation Notes

1. **TEDDI HTML-Driven**: Endpoint reverse-engineered. Parser may need updates if TEDDI UI changes.
2. **Async-First**: All core methods async. Use `asyncio.run()` for sync wrappers.
3. **Cache Validation**: Tests auto-cache in `tests/.cache/teddi_http.sqlite3`.
