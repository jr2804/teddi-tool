# TEDDI Tool

Search the [ETSI TEDDI](https://webapp.etsi.org/Teddi/) terminology database from
the command line or through an MCP server for AI agents.

## Overview

TEDDI Tool wraps ETSI's TErms and Definitions Database Interactive (TEDDI) in two
interfaces that share one async client, parser and output layer:

- **CLI** — `search-term` and `list-bodies` with table, JSON, ISON and TOON
  output.
- **MCP server** — `search_teddi`, `get_term_info` and `list_technical_bodies`
  tools for Claude, OpenCode and other MCP clients.

Requests go through a local SQLite cache (hishel) with a two-hour TTL, and the
scraped HTML is parsed into typed `TermResult`/`DocumentRef` dataclasses. The
technical-body filter accepts all 115 codes published by the TEDDI search form,
case-insensitively.

## Requirements

Python 3.13+ and network access to `webapp.etsi.org`. No account or API key is
needed.

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
mise install     # pinned toolchain
mise dev         # uv sync -U --dev --all-extras --all-groups
```

## Quick Start

```bash
# Exact-match lookup
teddi search-term "QoS" --pattern exactmatch

# Search definitions only, JSON output
teddi search-term "QoS" --scope definitions --output json

# Filter by technical bodies (codes are case-insensitive)
teddi search-term "test" --technical-bodies "3gpp,stq"

# List the 115 supported technical bodies
teddi list-bodies

# Start the MCP server on stdio
teddi-mcp
```

`teddi-tool` (primary) and `teddi` are the same CLI; `teddi-cli` is kept as an
alias for existing scripts and `teddi-mcp` starts the server directly.

## MCP Client Configuration

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

- [Usage](usage.md) — CLI options, output formats, MCP tools
- [Development](development.md) — setup, architecture, release process
- [API Reference](reference/api.md) — models, client, parser
- [Contributing](contributing.md)

## License

MIT — see [LICENSE](license.md).
