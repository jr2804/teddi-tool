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
| `uv` | Always | Environment sync (`uv sync --all-extras`) and every command (`uv run …`, `uvx …`) |
| `mise` | Running project tasks | Task runner reading `.config/mise/conf.d/*.toml` |
| `ruff` | Before finishing any edit | Lint + import sorting + formatting (`ruff.toml`) |
| `ty` | After changing types or signatures | Static type check (`ty.toml`, warnings are errors) |
| `pytest` | After behaviour changes | Test suite; `asyncio_mode = "auto"` |
| `undersort` | `mise run format` | Orders class members (public/protected/private) |
| `mdformat` | `mise run format-md` | Markdown formatting (not enforced in CI) |
| `cytoscnpy` | `mise run analyze` | Secrets/danger/quality scan of code and tests |
| `bun` / `bun x skills` | `mise run add-skills` | Installs agent skills from upstream repos |
| `bun x add-mcp` | `mise run add-mcp-servers` | Registers MCP servers with an AI client |

## MCP servers

| Server | When | Purpose |
| ------ | ---- | ------- |
| `teddi-mcp` (this repo) | Querying TEDDI from an MCP client | Tools `search_teddi`, `get_term_info`, `list_technical_bodies`; stdio transport |
| `cytoscnpy-mcp` | Agent-driven static analysis | Registered via `mise run add-mcp-servers`; runs `cytoscnpy mcp-server` |

## Skills

| Skill | When | Purpose |
| ----- | ---- | ------- |
| `cli-teddi` (`skills/cli-teddi/SKILL.md`) | Terminal TEDDI searches | `uv run teddi-cli term|list-bodies` recipes and filters |
| `mcp-teddi` (`skills/mcp-teddi/SKILL.md`) | MCP-client TEDDI lookups | Tool arguments, TB filtering, multi-definition behaviour |

## Project scripts & tasks

| Command | Purpose |
| ------- | ------- |
| `mise run format` | `undersort` + ruff import sort + `ruff format` on `src/ tests/` |
| `mise run format-md` | `mdformat` across the repo, excluding `.config/` |
| `mise run lint` | `ruff check` (stale target paths — see `.agents/POLICIES.md` → Verification) |
| `mise run lint-fix` / `lint-fix-unsafe` | `ruff check --fix` / `--unsafe-fixes` (same stale paths) |
| `mise run analyze` | `cytoscnpy . --secrets --danger --quality --include-tests` |
| `mise run env-sync` | `uv sync -U --dev --all-extras --all-groups` |
| `mise run upgrade-tools` | `mise install && mise up && mise prune` |
| `mise run add-skills` | Install upstream agent skills |
| `mise run add-mcp-servers` | Register MCP servers with a chosen AI client |
