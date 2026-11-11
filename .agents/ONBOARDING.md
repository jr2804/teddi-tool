# AGENTS.md — ONBOARDING

Read this when starting a new session. After first read, only revisit when
project structure or tooling changes significantly.

## Project

`teddi-tool` — Cyclopts CLI and FastMCP server for ETSI TEDDI term/abbreviation
lookup. Distributed on PyPI, documented at
<https://jr2804.github.io/teddi-tool/>. Full docs at `README.md` and `docs/`.

## Quick start

```bash
mise install                        # pinned tools (uv, ruff, ty, rumdl, ...)
mise dev                            # uv sync -U --dev --all-extras --all-groups
mise test                           # pytest with coverage
mise lint                           # ruff check --fix --unsafe-fixes
mise lint-check                     # ruff check (CI mode)
mise typecheck                      # ty check
mise spell                          # codespell
mise format                         # pyreorder + ruff format + import sort
mise docs                           # zensical build
mise all                            # everything above
```

Direct commands also work: `uv run pytest tests/ -v`, `uv run ruff check
src/ tests/`, `uv run ty check`.

## Entry points (read these first)

| File | Why |
|------|-----|
| `AGENTS.md` | Root rail — rules + `.agents/` index |
| `.agents/POLICIES.md` | Boundaries, priorities, verification |
| `.agents/FILES.md` | Source-of-truth locations |
| `src/teddi_tool/AGENTS.md` | Contracts for the package you are editing |
| `tests/AGENTS.md` | Test conventions |

## Where to dig deeper

- `docs/` — `index.md`, `usage.md`, `reference/api.md`, `development.md`
- `.agents/TOOLS.md` — tools, MCP servers, skills, CLIs in use
- `.agents/HISTORY.md` — past decisions and rationale
- `skills/teddi/SKILL.md` — task-level usage recipes for CLI and MCP

## Executables

| Command | Module | Purpose |
|---------|--------|---------|
| `teddi-tool`, `teddi` | `src/teddi_tool/cli/app.py` | Search, `list-bodies`, `server` |
| `teddi-cli` | `src/teddi_tool/cli/app.py` | Alias kept for existing scripts |
| `teddi-mcp` | `src/teddi_tool/server.py` | MCP server (stdio) |

## Available tools

Development tools, MCP servers, skills, and CLIs are inventoried in the
state file `.agents/TOOLS.md` — read it before assuming a tool, update it
when tooling changes. If tooling grows large, detail moves to
`.agents/tools/<name>.md` (each listed in TOOLS.md).

## Project lifecycle

- Releases: push a `v*` tag; `.github/workflows/release.yml` builds, writes
  LLM release notes (`scripts/release_notes.py`), creates the GitHub release,
  and publishes to PyPI via OIDC trusted publishing.
- Template: generated from copier-uv-plus; `.copier-answers.yml` drives
  `copier update`.
