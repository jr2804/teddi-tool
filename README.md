# TEDDI-MCP: FastMCP Server for ETSI TEDDI

A FastMCP 3.0 server that wraps ETSI's TErms and Definitions Database Interactive (TEDDI) for AI agent integration and command-line usage.

## Features

- **FastMCP 3.0 Server**: Expose TEDDI search as an MCP tool for AI agents (Claude, etc.)
- **CLI Interface**: Search TEDDI from the command line with table, JSON, ISON, and TOON output
- **HTTP Caching**: Automatic hishel-based caching of TEDDI responses (2-hour TTL)
- **TB Grouping**: Smart parsing of sub-table results with technical body grouping logic
- **Type-Safe**: Full Pydantic models and type hints throughout
- **Async-First**: Built on asyncio for performance

## Quick Start

### Installation

```bash
cd src/teddi-mcp
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

Then configure your AI agent client (e.g., Claude) to use this server:

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

- **models.py**: Pydantic data models (SearchIn, SearchPattern, TechnicalBody enums)
- **client.py**: Core TeddiClient with Protocol-based abstraction
- **parser.py**: HTML parsing with TB grouping logic
- **http_client.py**: HTTP session manager with hishel caching
- **search_utils.py**: Shared search logic for CLI executables
- **cli.py**: Typer CLI for `teddi` executable (full CLI)
- **search_cli.py**: Typer CLI for `teddi-cli` executable (search-only)
- **server.py**: FastMCP 3.0 server implementation

## Testing

```bash
# Run all tests
uv run pytest tests/teddi_mcp/ -v

# Run with coverage
uv run pytest tests/teddi_mcp/ --cov=teddi_mcp --cov-report=term-missing

# Run specific test
uv run pytest tests/teddi_mcp/test_parser.py -v
```

## Development

See [docs/development.md](docs/development.md) for setup, tests, and code
quality. Area contracts live next to the code:

- [`src/teddi_mcp/AGENTS.md`](src/teddi_mcp/AGENTS.md) — client, parser, CLI/MCP surface, adding features
- [`tests/AGENTS.md`](tests/AGENTS.md) — test conventions
- [`.agents/ONBOARDING.md`](.agents/ONBOARDING.md) — entry points and commands

## License

MIT
