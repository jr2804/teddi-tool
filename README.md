# TEDDI Tool

[![PyPI](https://img.shields.io/pypi/v/teddi-tool.svg)](https://pypi.org/project/teddi-tool/)
[![Python](https://img.shields.io/pypi/pyversions/teddi-tool.svg)](https://pypi.org/project/teddi-tool/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/jr2804/teddi-tool/actions/workflows/ci.yml/badge.svg)](https://github.com/jr2804/teddi-tool/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://jr2804.github.io/teddi-tool/)

CLI and FastMCP server for the ETSI [TEDDI](https://webapp.etsi.org/Teddi/)
terminology database.

## Features

- **CLI** — `teddi search-term` / `teddi list-bodies` with table, JSON, ISON, and
  TOON output
- **MCP server** — `search_teddi`, `get_term_info`, and `list_technical_bodies`
  tools for AI agents
- **HTTP caching** — hishel/SQLite cache with a two-hour TTL
- **Type-safe** — Pydantic models and full annotations
- **Async-first** — one async client shared by both interfaces

## Installation

```bash
uv tool install teddi-tool      # or: pipx install teddi-tool
```

From source:

```bash
git clone https://github.com/jr2804/teddi-tool.git
cd teddi-tool
mise dev
```

## Usage

```bash
teddi search-term "QoS" --pattern exactmatch
teddi search-term "QoS" --scope definitions --output json
teddi search-term "test" --technical-bodies "3gpp,stq"
teddi list-bodies
teddi-mcp        # MCP server on stdio
```

`teddi-tool` and `teddi` are the same CLI; `teddi-cli` is an alias kept for
existing scripts.

### MCP client configuration

```json
{
  "mcpServers": {
    "teddi": {
      "command": "teddi-mcp"
    }
  }
}
```

## Architecture

| Module | Responsibility |
|--------|----------------|
| `src/teddi_tool/models.py` | Pydantic models and enums |
| `src/teddi_tool/client.py` | `TeddiClient` and the `TeddiSource` protocol |
| `src/teddi_tool/http_client.py` | Cached httpx2 client factory |
| `src/teddi_tool/parser.py` | TEDDI HTML parsing |
| `src/teddi_tool/search_utils.py` | Shared search/output helpers |
| `src/teddi_tool/cli/` | Cyclopts CLI |
| `src/teddi_tool/server.py` | FastMCP server |

## Development

```bash
mise dev        # install tools and sync dev dependencies
mise test       # pytest with coverage
mise all        # test, lint, spell, format, docs
```

See [`docs/development.md`](docs/development.md) for setup and release notes.
Area contracts live next to the code:

- [`src/teddi_tool/AGENTS.md`](src/teddi_tool/AGENTS.md) — client, parser, CLI/MCP surface
- [`tests/AGENTS.md`](tests/AGENTS.md) — test conventions
- [`.agents/ONBOARDING.md`](.agents/ONBOARDING.md) — entry points and commands

## License

MIT
