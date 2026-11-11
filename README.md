# TEDDI Tool

[![PyPI](https://img.shields.io/pypi/v/teddi-tool.svg)](https://pypi.org/project/teddi-tool/)
[![Python](https://img.shields.io/pypi/pyversions/teddi-tool.svg)](https://pypi.org/project/teddi-tool/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/jr2804/teddi-tool/actions/workflows/ci.yml/badge.svg)](https://github.com/jr2804/teddi-tool/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://jr2804.github.io/teddi-tool/)

Search the ETSI [TEDDI](https://webapp.etsi.org/Teddi/) terminology database from
the terminal or expose it to AI agents as an MCP server. One async client, one
parser and one output layer serve both interfaces.

```bash
uv tool install teddi-tool
teddi search-term "QoS" --pattern exactmatch
```

## Features

- **CLI** — `search-term` (term, scope, pattern, technical-body filter) and
  `list-bodies`, with table, JSON, ISON and TOON output.
- **MCP server** — `search_teddi`, `get_term_info` and `list_technical_bodies`
  tools over stdio; no extra service to deploy.
- **All 115 TEDDI technical bodies** — filters are matched case-insensitively and
  validated against the codes published by the TEDDI search form.
- **Local HTTP cache** — hishel/SQLite store with a two-hour TTL, so repeated
  lookups do not hit ETSI.
- **Typed core** — dataclasses and `StrEnum` enums with full annotations, plus a
  `TeddiSource` protocol that keeps the client mockable.
- **Async-first** — a single `httpx2` client shared by the CLI and MCP server.

## Requirements

Python 3.13 or newer. TEDDI itself is a public ETSI web application; no account
or API key is required.

## Installation

```bash
# with uv (recommended)
uv tool install teddi-tool

# or with pipx
pipx install teddi-tool
```

From a checkout (requires [mise](https://mise.jdx.dev/)):

```bash
git clone https://github.com/jr2804/teddi-tool.git
cd teddi-tool
mise install     # pinned toolchain: ruff, ty, rumdl, pyreorder, ...
mise dev         # uv sync -U --dev --all-extras --all-groups
```

## Usage

```bash
teddi search-term "QoS"                              # rich table (default)
teddi search-term "QoS" --pattern exactmatch         # exact match
teddi search-term "QoS" --scope definitions -o json  # definitions only, JSON
teddi search-term "test" -t "3gpp,stq"               # filter technical bodies
teddi list-bodies                                    # 115 valid TB codes
teddi-mcp                                            # MCP server on stdio
```

Scope values: `abbreviations`, `definitions`, `both` (default). Pattern values:
`alloccurrences` (default), `exactmatch`, `startingwith`, `endingwith`. Output
formats: `table`, `json`, `ison`, `toon`. Every option can also be set through
`TEDDI_TOOL_SCOPE`, `TEDDI_TOOL_PATTERN`, `TEDDI_TOOL_TECHNICAL_BODIES` and
`TEDDI_TOOL_OUTPUT`.

`teddi-tool` and `teddi` are the same CLI; `teddi-cli` is an alias kept for
existing scripts, and `teddi-mcp`/`teddi server` start the MCP server directly.

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

## Documentation

- [Usage](https://jr2804.github.io/teddi-tool/usage/) — CLI options, output
  formats, MCP tools
- [API reference](https://jr2804.github.io/teddi-tool/reference/api/) — models,
  client, parser
- [Development](https://jr2804.github.io/teddi-tool/development/) — setup,
  architecture, release process

## Architecture

| Module | Responsibility |
|--------|----------------|
| `src/teddi_tool/models.py` | Dataclasses, enums, and `TECHNICAL_BODY_CODES` |
| `src/teddi_tool/client.py` | `TeddiClient` and the `TeddiSource` protocol |
| `src/teddi_tool/http_client.py` | Cached `httpx2` client factory (hishel) |
| `src/teddi_tool/parser.py` | TEDDI HTML parsing and TB grouping |
| `src/teddi_tool/search_utils.py` | Shared search execution and output rendering |
| `src/teddi_tool/cli/` | Cyclopts CLI (`app.py`, `commands.py`, `args.py`) |
| `src/teddi_tool/server.py` | FastMCP server |

## Development

```bash
mise install    # install the pinned toolchain
mise dev        # sync all dependency groups
mise test       # pytest with coverage
mise all        # test, lint, spell, format, format-md, docs
```

Run `mise typecheck` separately; `mise all` does not include it. See
[`docs/development.md`](docs/development.md) for the full task list and the
release process. Area contracts live next to the code:

- [`src/teddi_tool/AGENTS.md`](src/teddi_tool/AGENTS.md) — client, parser, CLI/MCP
  surface
- [`tests/AGENTS.md`](tests/AGENTS.md) — test conventions
- [`.agents/ONBOARDING.md`](.agents/ONBOARDING.md) — entry points and commands

## Contributing

Issues and pull requests are welcome; see
[`docs/contributing.md`](docs/contributing.md) and the
[Code of Conduct](docs/code_of_conduct.md).

## License

MIT — see [`LICENSE`](LICENSE).
