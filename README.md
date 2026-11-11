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
- **All TEDDI technical bodies** — filters are matched case-insensitively and
  validated against the code list published by the TEDDI search form (fetched
  live, cached for 90 days, so new codes need no release).
- **Local HTTP cache** — hishel/SQLite store (2-hour search TTL, 90-day
  technical-body menu TTL), so repeated lookups do not hit ETSI; both TTLs are
  configurable.
- **Typed core** — dataclasses and `StrEnum` enums with full annotations, plus a
  `TeddiSource` protocol that keeps the client mockable.
- **Async-first** — an async `httpx2` core shared by the CLI and MCP server.

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
teddi list-bodies                                    # valid TB codes from TEDDI
teddi-mcp                                            # MCP server on stdio
```

Scope values: `abbreviations`, `definitions`, `both` (default). Pattern values:
`alloccurrences` (default), `exactmatch`, `startingwith`, `endingwith`. Output
formats: `table`, `json`, `ison`, `toon`. Cache lifetimes are tuned with
`--cache-ttl`/`--menu-cache-ttl` (seconds). Every option can also be set through
the `TEDDI_TOOL_` environment variables of the same name — `TEDDI_TOOL_SCOPE`,
`TEDDI_TOOL_PATTERN`, `TEDDI_TOOL_TECHNICAL_BODIES`, `TEDDI_TOOL_OUTPUT`,
`TEDDI_TOOL_CACHE_TTL` and `TEDDI_TOOL_MENU_CACHE_TTL`.

`teddi-tool` and `teddi` are the same CLI; `teddi-cli` is an alias kept for
existing scripts, and `teddi-mcp`/`teddi server` start the MCP server directly.

### MCP client configuration

```json
{
  "mcpServers": {
    "teddi": {
      "command": "teddi-mcp",
      "env": {
        "TEDDI_TOOL_CACHE_TTL": "3600",
        "TEDDI_TOOL_MENU_CACHE_TTL": "604800"
      }
    }
  }
}
```

The `env` block is optional; it tunes the search-response and technical-body
menu cache lifetimes in seconds.

## Documentation

- [Usage](https://jr2804.github.io/teddi-tool/usage/) — CLI options, output
  formats, MCP tools
- [API reference](https://jr2804.github.io/teddi-tool/reference/api/) — models,
  client, parser
- [Development](https://jr2804.github.io/teddi-tool/development/) — setup,
  project layout, tasks and release process

## Contributing

Issues and pull requests are welcome; see
[`docs/contributing.md`](docs/contributing.md) and the
[Code of Conduct](docs/code_of_conduct.md).

## License

MIT — see [`LICENSE`](LICENSE).
