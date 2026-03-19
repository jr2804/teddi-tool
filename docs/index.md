# TEDDI-MCP

FastMCP 3.0 server for ETSI TEDDI (TErms and Definitions Database Interactive).

## Overview

A FastMCP 3.0 server that wraps ETSI's TEDDI for AI agent integration and command-line usage.

## Features

- **FastMCP 3.0 Server**: Expose TEDDI search as an MCP tool for AI agents
- **CLI Interface**: Search TEDDI from the command line with table, JSON, ISON, and TOON output
- **HTTP Caching**: Automatic hishel-based caching of TEDDI responses (2-hour TTL)
- **TB Grouping**: Smart parsing of sub-table results with technical body grouping logic
- **Type-Safe**: Full Pydantic models and type hints throughout
- **Async-First**: Built on asyncio for performance

## Quick Start

### Installation

```bash
cd teddi-mcp
uv sync --all-extras
uv pip install -e .
```

### CLI Usage

```bash
# Search for a term
teddi-mcp search term "QoS" --search-pattern exactmatch

# List available technical bodies
teddi-mcp search list-bodies

# JSON output
teddi-mcp search term "QoS" --output json

# ISON output (token-optimized)
teddi-mcp search term "QoS" --output ison

# TOON output (token-optimized)
teddi-mcp search term "QoS" --output toon

# Filter by technical bodies
teddi-mcp search term "test" --technical-bodies "3gpp,etsi"
```

### MCP Server

```bash
# Start the MCP server (stdio)
teddi-mcp server
```

Then configure your AI agent client to use this server:

```json
{
  "mcpServers": {
    "teddi": {
      "command": "teddi-mcp",
      "args": ["server"]
    }
  }
}
```

## Documentation

- [Usage](usage.md) - Detailed CLI and MCP usage
- [Development](development.md) - Development guidelines
- [API Reference](api.md) - API documentation

## License

MIT
