# tests — AGENTS.md

## Purpose

Pytest suite pinning the parser's TEDDI table handling, client request
shaping, and model validation. Repo-wide rules are in the root `AGENTS.md`.

## Ownership

Everything under `tests/`. Shared fixtures live in `tests/conftest.py`;
production behaviour is owned by `src/teddi_mcp/AGENTS.md`.

## Local Contracts

- Import production code as `src.teddi_mcp.<module>` (e.g. `from src.teddi_mcp.parser import parse_teddi_response`). Package-internal imports use `teddi_mcp.*` — do not "normalise" test imports to match.
- No network calls. Inject a mock client into `TeddiClient(client=AsyncMock())` and set `post.return_value.text` to inline HTML, following `tests/test_client.py`.
- `asyncio_mode = "auto"` (`pyproject.toml`), so plain `async def` tests run without a marker. Existing `@pytest.mark.asyncio` markers are redundant — keep the style of the file you edit.
- Fixtures available: `cache_dir` (temporary `.cache` under `tmp_path`) and `test_data_dir` (`tests/fixtures`). The `tests/fixtures/` directory does not exist yet — create it before relying on `test_data_dir`.
- There is no `tests/__init__.py`-based package layout dependency; modules are collected by `testpaths = ["tests"]`.
- Coverage config is `[tool.coverage.*]` in `pyproject.toml` with `source = ["teddi_mcp"]`.

## Work Guidance

- Parser coverage: one test per TEDDI table shape — flat row, nested document sub-table, empty TB cell inheritance, multi-document cell.
- Client coverage: assert the form payload (`qWhatToSearch`, `qWhereOption`, `qWhatOption`, `qShowTBs`), not just the returned count.
- CLI/MCP coverage: assert argument plumbing and serialized output; do not re-test HTTP behaviour there.
- Keep HTML fixtures inline for single cases; move to `tests/fixtures/` once a payload is reused.

## Verification

```bash
uv run pytest tests/ -v
uv run pytest tests/ --cov=teddi_mcp --cov-report=term-missing
```

## Child DOX Index

None.
