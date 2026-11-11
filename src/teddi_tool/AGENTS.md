# src/teddi_tool — AGENTS.md

## Purpose

The whole product: Pydantic models, a cached HTTP client over ETSI TEDDI's
scraped search form, an HTML parser, shared search/output helpers, a Cyclopts
CLI, and a FastMCP server. Repo-wide rules are in the root `AGENTS.md`.

## Ownership

Every module in this directory, plus the console scripts declared in
`pyproject.toml`. Root `AGENTS.md` owns project-wide rules; root `.agents/`
owns tooling and path inventories.

## Local Contracts

- `TeddiSource` (`src/teddi_tool/client.py:38`) is the seam between consumers and TEDDI.
  Type new consumers against it, not against `TeddiClient`.
- `TeddiClient` is an async context manager: `__aenter__` creates the cached httpx2 client only
  when none was injected, and `__aexit__` closes only a client it owns
  (`src/teddi_tool/client.py:93`–`104`). `_get_client()` raises `RuntimeError` outside the
  context.
- Search request shape (`src/teddi_tool/client.py:122`–`145`): `POST TEDDI_SEARCH_URL`
  (`https://webapp.etsi.org/Teddi/Main.asp`) with form fields `qWhatToSearch`, `qWhatOption`
  (from `SEARCH_IN_TO_PARAM`), `qWhereOption` (from `SEARCH_PATTERN_TO_PARAM`), `qShowTBs`
  (comma-joined codes in TEDDI casing, `ALL` when the filter is `all` or empty),
  plus `btnSearch.x` / `btnSearch.y`.
- `get_available_technical_bodies()` GETs `TEDDI_MENU_URL`
  (`https://webapp.etsi.org/Teddi/Menu.asp`) and parses `select[name=qShowTBs]` via
  `parse_technical_bodies_page` — no fallback list exists, HTTP/parse errors propagate
  (`src/teddi_tool/client.py:157`–`180`). The menu client uses its own hishel cache with
  a configurable TTL (`menu_cache_ttl`, default `TEDDI_MENU_CACHE_TTL` = 90 days), so the
  code list survives long offline periods between releases. `execute_search` feeds this
  list to `parse_technical_bodies`, so new TEDDI codes validate without a release; a
  failed menu fetch aborts the search.
- Cache contract (`src/teddi_tool/http_client.py:13`): hishel `AsyncSqliteStorage`,
  `.cache/teddi_http.sqlite3` by default, TTL fixed at write time (`cache_ttl`, default
  `SEARCH_CACHE_TTL` = 2 h; hishel 2.x has no refresh-on-access), 30 s timeout, browser
  User-Agent. There is no retry transport. Both TTLs are configurable end to end:
  `TeddiClient`/`execute_search`/`execute_list_bodies` kwargs, CLI `--cache-ttl` /
  `--menu-cache-ttl` (env `TEDDI_TOOL_CACHE_TTL` / `TEDDI_TOOL_MENU_CACHE_TTL`), and the
  MCP server reads the same env vars in `main()`.
- Parser (`src/teddi_tool/parser.py`): `parse_teddi_response(html)` returns `list[TermResult]`;
  an empty TB cell inherits the previous row's technical body; document sub-tables become
  `DocumentRef` entries.
- Output path: `build_results_payload` → `serialize_payload` (`OutputFormat`: table default,
  `json`, `ison`, `toon`) in `src/teddi_tool/search_utils.py`; `render_table` uses `rich`.
- MCP tools (`src/teddi_tool/server.py`): `search_teddi`, `get_term_info`,
  `list_technical_bodies`. Payload shape and TB-filter parsing come from `search_utils`
  (`build_results_payload`, `parse_technical_bodies`) — do not re-implement them here.
  `fetch_document()` exists on the client but is intentionally not exposed as a tool or command.
- CLI surface: `teddi-tool`/`teddi` `search-term|list-bodies|server` and the
  `teddi-cli` alias (`src/teddi_tool/cli/app.py`, `commands.py`). Commands
  delegate to `search_utils` and share option aliases from
  `src/teddi_tool/cli/args.py`.

## Work Guidance

- Adding or changing a search field touches five layers in one change: enum/field in `models.py`
  → TEDDI param mapping or form field in `client.py` → CLI option (`cli/args.py` +
  `cli/commands.py`, via `search_utils.py`) → MCP tool argument (`server.py`) → tests.
- Adding an output format: extend `OutputFormat` in `models.py`, implement in
  `serialize_payload`, then assert the new branch in `tests/test_search_utils.py` (create it if
  absent).
- Responses that cannot be parsed raise `ValueError`; HTTP failures propagate as `httpx2.HTTPError`. Do not swallow either at the client layer.
- Log through the module-level `logger`; request payloads stay at `DEBUG` so term content is not logged at default levels.
- Never re-order the `[project.scripts]` entries in `pyproject.toml` — console-script name changes are user-facing breakage.

## Verification

```bash
mise test
mise lint-check
mise typecheck
```

## Child DOX Index

No child AGENTS.md below this directory yet. Add one only when a subpackage
grows its own durable contract; list it here.
