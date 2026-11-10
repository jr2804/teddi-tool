# AGENTS.md — ONBOARDING

Read this when starting a new session. After first read, only revisit when
project structure or tooling changes significantly.

## Project

FastMCP 3.0 server plus Typer CLIs for ETSI TEDDI term/abbreviation lookup.
Full docs at `README.md` and `docs/`.

## Quick start

```bash
uv sync --all-extras                # sync environment
uv run pytest tests/ -v             # tests
uv run ruff check src/ tests/       # lint
uv run ruff format --check src/ tests/
uv run ty check                     # type check
mise run format                     # undersort + ruff import sort/format
mise run format-md                  # markdown format
mise run analyze                    # cytoscnpy quality/secrets scan
```

There is no `test` or `typecheck` task in `.config/mise/conf.d/` — use the
`uv run` commands above.

## Entry points (read these first)

| File | Why |
|------|-----|
| `AGENTS.md` | Root rail — rules + `.agents/` index |
| `.agents/POLICIES.md` | Boundaries, priorities, verification |
| `.agents/FILES.md` | Source-of-truth locations |
| `src/teddi_mcp/AGENTS.md` | Contracts for the package you are editing |
| `tests/AGENTS.md` | Test conventions |

## Where to dig deeper

- `docs/` — `index.md`, `usage.md`, `api.md`, `development.md`
- `.agents/TOOLS.md` — tools, MCP servers, skills, CLIs in use
- `.agents/HISTORY.md` — past decisions and rationale
- `skills/cli-teddi/SKILL.md`, `skills/mcp-teddi/SKILL.md` — task-level usage recipes

## Executables

| Command | Module | Purpose |
|---------|--------|---------|
| `teddi` | `src/teddi_mcp/cli.py` | Search, `list-bodies`, `server` |
| `teddi-cli` | `src/teddi_mcp/search_cli.py` | Search-only CLI |
| `teddi-mcp` | `src/teddi_mcp/server.py` | MCP server (stdio) |

## Available tools

Development tools, MCP servers, skills, and CLIs are inventoried in the
state file `.agents/TOOLS.md` — read it before assuming a tool, update it
when tooling changes. If tooling grows large, detail moves to
`.agents/tools/<name>.md` (each listed in TOOLS.md).
