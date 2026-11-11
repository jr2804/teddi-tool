# Development Guide

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/jr2804/teddi-tool.git
   cd teddi-tool
   ```

2. Install pinned tools and sync dependencies (Python 3.13+, `uv`, `mise`):

   ```bash
   mise install     # toolchain from .config/mise/config.toml
   mise dev         # uv sync -U --dev --all-extras --all-groups
   ```

## Tasks

| Task | Purpose |
|------|---------|
| `mise dev` | Sync all dependency groups |
| `mise test` | `pytest --cov=teddi_tool` |
| `mise lint` | `ruff check src/ tests/ --fix --unsafe-fixes` |
| `mise lint-check` | `ruff check src/ tests/` without fixes |
| `mise typecheck` | `ty check src/ tests/` |
| `mise spell` | `codespell src/ tests/` |
| `mise format` | `pyreorder`, `ruff format`, import sort |
| `mise format-md` | `rumdl` over Markdown |
| `mise docs` | Build the Zensical site |
| `mise release-notes` | Generate notes for the latest tag |
| `mise clean` | Remove build artefacts and caches |
| `mise all` | `test`, `lint`, `spell`, `format`, `format-md`, `docs` |

`mise all` does not run `mise typecheck`; run it in the same pass (CI does).

Run a single test file directly:

```bash
uv run pytest tests/test_parser.py -v
```

Tests never call TEDDI. Client tests inject an `AsyncMock` in place of
`httpx2.AsyncClient` (see `tests/test_client.py`); `tests/test_http_client.py`
inspects the cache factory's storage, timeout and headers instead of performing
requests. Cache paths use the `cache_dir` fixture, never the repository
`.cache/`.

## Code Quality

```bash
uv run ruff check src/ tests/          # lint only
uv run ruff format --check src/ tests/
uv run ty check src/ tests/
```

`ruff.toml` and `ty.toml` are the sources of truth; both target Python 3.13.
`mise lint` applies fixes, so use `mise lint-check` (or the `uv run` command
above) when you want a read-only check.

## Project Layout

The package lives in `src/teddi_tool/`; module-level contracts are documented
in [`src/teddi_tool/AGENTS.md`](https://github.com/jr2804/teddi-tool/blob/main/src/teddi_tool/AGENTS.md)
and test conventions in
[`tests/AGENTS.md`](https://github.com/jr2804/teddi-tool/blob/main/tests/AGENTS.md).
For a current file list, run `rg --files` instead of relying on a checked-in
tree.

| Module | Responsibility |
|--------|----------------|
| `models.py` | Dataclasses, `StrEnum` enums and `TECHNICAL_BODY_CODES` |
| `client.py` | `TeddiSource` protocol and `TeddiClient` |
| `parser.py` | TEDDI HTML parsing with TB grouping |
| `http_client.py` | hishel-cached `httpx2` client factory |
| `search_utils.py` | Shared search execution and output rendering |
| `cli/app.py`, `cli/commands.py`, `cli/args.py` | Cyclopts entry point, commands, option aliases |
| `server.py` | FastMCP server |

## Key Design Patterns

### Protocol-Based Abstraction

`TeddiSource` (`src/teddi_tool/client.py`) is the seam between consumers and
TEDDI, which keeps the client mockable:

```python
class TeddiSource(Protocol):
    async def search_terms(self, request: SearchRequest) -> SearchResponse: ...
    async def get_available_technical_bodies(self) -> list[str]: ...
    async def fetch_document(self, url: str) -> bytes: ...
```

`TeddiClient` implements it and must be used as an async context manager.

### HTTP Caching

Requests go through `create_cached_teddi_async_client()`:

- SQLite store: `.cache/teddi_http.sqlite3` (or the given `cache_dir`)
- TTL: 2 hours, fixed when the entry is written (hishel 2.x has no
  refresh-on-access)
- 30 s timeout, browser User-Agent

There is no retry transport; failed requests surface as `httpx2.HTTPError`.

### TEDDI Search Form

Search submits a form to `https://webapp.etsi.org/Teddi/Main.asp`:

| Field | Meaning |
|-------|---------|
| `qWhatToSearch` | Search term |
| `qWhatOption` | Scope: `1` abbreviations, `2` definitions, `3` both |
| `qWhereOption` | Pattern: `1` exact, `2` all occurrences, `3` starting with, `4` ending with |
| `qShowTBs` | Comma-separated TB codes, or `ALL` |

The list behind `qShowTBs` lives in `https://webapp.etsi.org/Teddi/Menu.asp`.
`TeddiClient.get_available_technical_bodies()` parses that menu and falls back to
the bundled `TECHNICAL_BODY_CODES` when the page is unavailable.

### TB Grouping in Parser

TEDDI results use nested tables. The parser handles TB inheritance:

- Empty TB cell inherits the previous row's technical body
- Document sub-tables become `DocumentRef` entries

### Dual API: MCP + CLI

MCP tools and CLIs share the same execution path:

- `search_teddi` / `search-term` — search with filters
- `list_technical_bodies` / `list-bodies` — list technical bodies

`fetch_document()` exists on the client but is not exposed as a tool or
command.

## Adding Features

### New Search Filter

1. Define/extend the enum in `src/teddi_tool/models.py` (or add new codes to
   `TECHNICAL_BODY_CODES`)
2. Add the field to `SearchRequest`
3. Map it to a TEDDI form field in `src/teddi_tool/client.py`
4. Expose the option in `src/teddi_tool/cli/args.py` and use it in
   `src/teddi_tool/cli/commands.py`
5. Expose it in the MCP tool in `src/teddi_tool/server.py`
6. Add tests

## Releasing

Versions are CalVer: `YYYY.MM.N` (e.g. `2026.11.1`), where `N` counts releases
within the month. Versions come from git tags (`uv-dynamic-versioning`), so no
version string is edited by hand.

Every push to `main` triggers `.github/workflows/release.yml`:

1. Run the test suite on the commit; a failing build stops the release.
2. Compute the next calendar version and create the annotated tag when HEAD is
   not tagged yet.
3. Build sdist and wheel with `uv build` (the version comes from the new tag).
4. Generate release notes: `scripts/release_notes.py` summarizes the commits
   since the previous tag with an OpenAI-compatible chat endpoint when
   `OPENAI_API_KEY` (and optionally `OPENAI_BASE_URL`, `OPENAI_MODEL`) is set;
   otherwise the job falls back to a plain commit list.
5. Create the GitHub release named after the version.
6. Publish to PyPI with `pypa/gh-action-pypi-publish` using OIDC trusted
   publishing (no token stored). One-time setup: on PyPI, add a trusted
   publisher for `jr2804/teddi-tool` with workflow `release.yml` and
   environment `pypi`.

To release a commit that was already pushed without a version bump, re-run the
workflow from the Actions tab (`workflow_dispatch`). A commit whose tag already
exists is not published twice.

Run the notes script locally with:

```bash
uv run python scripts/release_notes.py --from-tag 2026.11.1
```

## Template Updates

The project is generated from
[copier-uv-plus](https://codeberg.org/jr2804/copier-uv-plus). Answers live in
`.copier-answers.yml`; apply upstream changes with:

```bash
uvx --with copier-templates-extensions copier update --trust --defaults
```

## Implementation Notes

1. **TEDDI HTML-driven**: the search form was reverse-engineered; the parser
   may need updates if the TEDDI UI changes.
2. **Async-first**: all client methods are `async`; the Cyclopts command
   wrappers call them via `asyncio.run()`.
3. **Offline tests**: cache paths in tests are temporary (`cache_dir`
   fixture), never the repository `.cache/`.
