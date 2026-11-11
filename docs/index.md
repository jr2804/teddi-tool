# TEDDI Tool

Search the [ETSI TEDDI](https://webapp.etsi.org/Teddi/) terminology database from
the command line or through an MCP server for AI agents.

## Overview

TEDDI Tool wraps ETSI's TErms and Definitions Database Interactive (TEDDI) in two
interfaces that share one async client, parser, and output layer:

- **CLI** — table, JSON, ISON, and TOON output for humans and scripts.
- **MCP server** — `search_teddi`, `get_term_info`, and `list_technical_bodies`
  tools for Claude, OpenCode, and other MCP clients.

Requests are cached in a local SQLite store (hishel) with a two-hour TTL, and the
scraped HTML is parsed into typed `TermResult`/`DocumentRef` objects.

## Installation

```bash
# with uv (recommended)
uv tool install teddi-tool

# or with pipx
pipx install teddi-tool
```

From a checkout:

```bash
git clone https://github.com/jr2804/teddi-tool.git
cd teddi-tool
mise dev
```

## Quick Start

```bash
# Exact-match lookup
teddi search-term "QoS" --pattern exactmatch

# Search definitions only, JSON output
teddi search-term "QoS" --scope definitions --output json

# Filter by technical bodies
teddi search-term "test" --technical-bodies "3gpp,etsi"

# List known technical bodies
teddi list-bodies

# Start the MCP server on stdio
teddi-mcp
```

`teddi-tool` (primary) and `teddi` are the same CLI; `teddi-mcp` starts the server
directly.

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

- [Usage](usage.md) — CLI commands, output formats, MCP tools
- [Development](development.md) — setup, architecture, release process
- [API Reference](reference/api.md) — models, client, parser
- [Contributing](contributing.md)

## License

MIT — see [LICENSE](license.md).
