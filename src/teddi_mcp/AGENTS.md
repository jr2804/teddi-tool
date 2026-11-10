# src/teddi_mcp — AGENTS.md

## Purpose

The whole product: Pydantic models, a cached HTTP client over ETSI TEDDI's
scraped search form, an HTML parser, shared search/output helpers, two Typer
CLIs, and a FastMCP server. Repo-wide rules are in the root `AGENTS.md`.

## Ownership

Every module in this directory, plus the console scripts declared in
`pyproject.toml`. Root `AGENTS.md` owns project-wide rules; root `.agents/`
owns tooling and path inventories.

## Local Contracts

- `TeddiSource` (`src/teddi_mcp/client.py:38`) is the seam between consumers and TEDDI. Type new consumers against it, not against `TeddiClient`.
- `TeddiClient` is an async context manager: `__aenter__` creates the cached httpx client only when none was injected, and `__aexit__` closes only a client it owns (`src/teddi_mcp/client.py:93`–`104`). `_get_client()` raises `RuntimeError` outside the context.
- Search request shape (`src/teddi_mcp/client.py:122`–`145`): `POST TEDDI_SEARCH_URL` (`https://webapp.etsi.org/Teddi/Main.asp`) with form fields `qWhatToSearch`, `qWhereOption` (from `SEARCH_IN_TO_PARAM`), `qWhatOption` (from `SEARCH_PATTERN_TO_PARAM`), `qShowTBs` (upper-cased `TechnicalBody` values joined by comma, `ALL` for `TechnicalBody.ALL`), plus `btnSearch.x` / `btnSearch.y`.
- `get_available_technical_bodies()` returns the static `TechnicalBody` enum minus `ALL` (`src/teddi_mcp/client.py:157`–`166`). TEDDI is not queried — enum additions must match real TEDDI TB codes.
- Cache contract (`src/teddi_mcp/http_client.py:13`–`56`): hishel `AsyncSqliteStorage`, `.cache/teddi_http.sqlite3` by default, `cache_ttl=7200`, refresh on access, 30 s timeout, browser User-Agent. There is no retry transport.
- Parser (`src/teddi_mcp/parser.py`): `parse_teddi_response(html)` returns `list[TermResult]`; an empty TB cell inherits the previous row's technical body; document sub-tables become `DocumentRef` entries.
- Output path: `build_results_payload` → `serialize_payload` (`OutputFormat`: table default, `json`, `ison`, `toon`) in `src/teddi_mcp/search_utils.py`; `render_table` uses `rich`.
- MCP tools (`src/teddi_mcp/server.py`): `search_teddi`, `get_term_info`, `list_technical_bodies`. `fetch_document()` exists on the client but is intentionally not exposed as a tool or command.
- CLI surface: `teddi search-term|list-bodies|server` (`src/teddi_mcp/cli.py`), `teddi-cli term|list-bodies` (`src/teddi_mcp/search_cli.py`). Both delegate to `search_utils`.

## Work Guidance

- Adding or changing a search field touches five layers in one change: enum/field in `models.py` → TEDDI param mapping or form field in `client.py` → CLI option (`cli.py` plus `search_cli.py` via `search_utils.py`) → MCP tool argument (`server.py`) → tests.
- Adding an output format: extend `OutputFormat` in `models.py`, implement in `serialize_payload`, then assert the new branch in `tests/test_search_utils.py` (create it if absent).
- Unparseable responses raise `ValueError`; HTTP failures propagate as `httpx.HTTPError`. Do not swallow either at the client layer.
- Log through the module-level `logger`; request payloads stay at `DEBUG` so term content is not logged at default levels.
- Never re-order the `[project.scripts]` entries in `pyproject.toml` — console-script name changes are user-facing breakage.

## Verification

```bash
uv run pytest tests/ -v
uv run ruff check src/ tests/
uv run ty check
```

## Child DOX Index

No child AGENTS.md below this directory yet. Add one only when a subpackage
grows its own durable contract; list it here.
