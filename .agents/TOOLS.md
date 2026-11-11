# AGENTS.md — TOOLS

State file: inventory of tools used in development — CLIs, MCP servers,
skills, runtimes, and project scripts. Demand-loaded like all state files;
keep it current (see `.agents/MAINTENANCE.md`).

## Rules

- Use an existing tool before adding a new one. No new tools, MCP servers,
  skills, or dependencies without explicit instruction (`.agents/POLICIES.md`).
- Each tool appears exactly once, in its primary table.
- Tables describe current usage — delete rows when tools leave; this is not a
  historical log.

## Subdirectory

If this file grows past its size budget, split detail into
`.agents/tools/<name>.md` — every file there MUST be listed above.

## CLI tools & runtimes

| Tool | When | Purpose |
| ---- | ---- | ------- |
| `uv` | Always | Environment sync (`uv sync --dev`) and every command (`uv run …`, `uvx …`) |
| `mise` | Running project tasks | Toolchain + task runner reading `.config/mise/conf.d/*.toml` |
| `ruff` | Before finishing any edit | Lint, import sorting, formatting (`ruff.toml`, py313) |
| `ty` | After changing types or signatures | Static type check (`ty.toml`, warnings are errors) |
| `pytest` | After behaviour changes | Test suite with coverage; `asyncio_mode = "auto"` |
| `pyreorder` | `mise format` | Orders class members (public/protected/private) |
| `rumdl` | `mise format-md` | Markdown lint/format |
| `codespell` | `mise spell` | Spelling check over `src/ tests/` |
| `zensical` | `mise docs` | Builds the documentation site (`zensical.toml`) |
| `bun` / `bun x skills` | `mise add-skills` | Installs agent skills from the CSV catalogue |
| `bun x add-mcp` | `mise add-mcp-servers <agent>` | Registers MCP servers with an AI client |

## MCP servers

| Server | When | Purpose |
| ------ | ---- | ------- |
| `teddi-mcp` (this repo) | Querying TEDDI from an MCP client | Tools `search_teddi`, `get_term_info`, `list_technical_bodies`; stdio transport |

## Skills

| Skill | When | Purpose |
| ----- | ---- | ------- |
| `cli-teddi` (`skills/cli-teddi/SKILL.md`) | Terminal TEDDI searches | `uv run teddi-tool search-term|list-bodies` recipes and filters |
| `mcp-teddi` (`skills/mcp-teddi/SKILL.md`) | MCP-client TEDDI lookups | Tool arguments, TB filtering, multi-definition behaviour |

## Project scripts & tasks

| Command | Purpose |
| ------- | ------- |
| `mise dev` | `uv sync -U --dev --all-extras --all-groups` |
| `mise test` | `uv run pytest --cov=teddi_tool` |
| `mise lint` | `ruff check src/ tests/ --fix --unsafe-fixes` |
| `mise lint-check` | `ruff check src/ tests/` (CI mode) |
| `mise typecheck` | `ty check src/ tests/` |
| `mise spell` | `codespell src/ tests/` |
| `mise format` | `pyreorder` + ruff import sort + `ruff format` on `src/ tests/` |
| `mise format-md` | `rumdl` over Markdown |
| `mise docs` | `zensical build` |
| `mise all` | test, lint, spell, format, format-md, docs |
| `mise release-notes` | `scripts/release_notes.py` via OpenAI-compatible endpoint |
| `mise clean` | Remove build, coverage, and docs artifacts |
| `mise add-mcp-servers <agent>` / `mise add-skills` | Install MCP servers / skills from the template catalogues |
