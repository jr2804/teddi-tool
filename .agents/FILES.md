# AGENTS.md — FILES

Single source of truth for paths, config keys, and naming conventions.
Kept compact — agents hallucinate less when they know where definitions live.

## Pattern

- One file owns each class of definition (paths, config defaults, enums).
- Import from that file. Never hard-code values in other modules.
- Variables that address files get `_file` suffix; directories get `_dir`.

## Project-specific sources of truth

| What | Where | Key names |
|------|-------|-----------|
| Pydantic models & enums | `src/teddi_mcp/models.py` | `SearchIn`, `SearchPattern`, `TechnicalBody`, `OutputFormat`, `SearchRequest`, `SearchResponse`, `TermResult`, `DocumentRef` |
| TEDDI endpoint URL | `src/teddi_mcp/client.py:26` | `TEDDI_SEARCH_URL` = `https://webapp.etsi.org/Teddi/Main.asp` |
| Enum → TEDDI form values | `src/teddi_mcp/client.py:29`–`38` | `SEARCH_IN_TO_PARAM`, `SEARCH_PATTERN_TO_PARAM` |
| TEDDI form field names | `src/teddi_mcp/client.py:122`–`140` | `qWhatToSearch`, `qWhereOption`, `qWhatOption`, `qShowTBs` |
| HTTP session + cache | `src/teddi_mcp/http_client.py:13` | `create_cached_teddi_async_client(cache_dir, cache_ttl=7200, refresh_ttl_on_access=True)`; DB `.cache/teddi_http.sqlite3` |
| HTML → models | `src/teddi_mcp/parser.py:15` | `parse_teddi_response(html_content)` |
| Source protocol / client | `src/teddi_mcp/client.py:38`, `:75` | `TeddiSource`, `TeddiClient` |
| Shared search + output | `src/teddi_mcp/search_utils.py` | `execute_search`, `execute_list_bodies`, `build_results_payload`, `serialize_payload`, `render_table` |
| Full CLI | `src/teddi_mcp/cli.py` | `search-term`, `list-bodies`, `server` commands |
| Search-only CLI | `src/teddi_mcp/search_cli.py` | `term`, `list-bodies` commands |
| MCP server & tools | `src/teddi_mcp/server.py` | `search_teddi`, `get_term_info`, `list_technical_bodies` |
| Console scripts | `pyproject.toml` → `[project.scripts]` | `teddi`, `teddi-cli`, `teddi-mcp` |
| Lint/format defaults | `ruff.toml` | `line-length = 100`, `pydocstyle.convention = "google"` |
| Type-check defaults | `ty.toml` | `python-version = "3.11"`, `error-on-warning = true` |
| Test config | `pyproject.toml` → `[tool.pytest.ini_options]`, `[tool.coverage.*]` | `asyncio_mode = "auto"`, `testpaths = ["tests"]` |
| Task definitions | `.config/mise/config.toml`, `.config/mise/conf.d/*.toml` | `format`, `format-md`, `lint`, `analyze`, `env-sync`, `upgrade-tools`, `add-skills`, `add-mcp-servers` |
| Project skills | `skills/cli-teddi/SKILL.md`, `skills/mcp-teddi/SKILL.md` | — |
| User docs | `docs/index.md`, `docs/usage.md`, `docs/api.md`, `docs/development.md` | — |

## Subdirectory

If this file grows past its size budget, split detail into
`.agents/files/<name>.md` — every file there MUST be listed above.
