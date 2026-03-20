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

Three executables are available:

```bash
# Full CLI (search + server)
teddi search-term "QoS" --pattern exactmatch
teddi list-bodies
teddi server

# Search-only CLI (equivalent to `teddi search-*`)
teddi-cli term "QoS" --pattern exactmatch
teddi-cli list-bodies

# MCP server only (equivalent to `teddi server`)
teddi-mcp
```

**Equivalences:**

| Command | Equivalent |
|---------|------------|
| `teddi-mcp` | `teddi server` |
| `teddi-cli term ...` | `teddi search-term ...` |
| `teddi-cli list-bodies` | `teddi list-bodies` |

**Output formats:**

```bash
# Table output (default)
teddi search-term "QoS"

# JSON output
teddi search-term "QoS" --output json

# ISON output (token-optimized)
teddi search-term "QoS" --output ison

# TOON output (token-optimized)
teddi search-term "QoS" --output toon

# Filter by technical bodies
teddi search-term "test" --technical-bodies "3gpp,etsi"
```

### MCP Server

```bash
# Start the MCP server (stdio)
teddi-mcp
```

Then configure your AI agent client to use this server:

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

- [Usage](usage.md) - Detailed CLI and MCP usage
- [Development](development.md) - Development guidelines
- [API Reference](api.md) - API documentation

## License

MIT
