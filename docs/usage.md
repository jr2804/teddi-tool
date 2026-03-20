# Usage

## CLI Executables

Three executables are provided:

| Executable | Description | Equivalent |
|------------|-------------|------------|
| `teddi` | Full CLI: search commands + server | — |
| `teddi-cli` | Search commands only | `teddi search-*` |
| `teddi-mcp` | MCP server only (stdio) | `teddi server` |

**Command Equivalences:**

| Command | Equivalent |
|---------|------------|
| `teddi-mcp` | `teddi server` |
| `teddi-cli term ...` | `teddi search-term ...` |
| `teddi-cli list-bodies` | `teddi list-bodies` |

## CLI Commands

### Search Terms

```bash
# Basic search (full CLI)
teddi search-term "QoS"

# Search (search-only CLI)
teddi-cli term "QoS"

# Exact match
teddi search-term "QoS" --pattern exactmatch

# Starting with
teddi search-term "QoS" --pattern startingwith

# Search in definitions only
teddi search-term "QoS" --scope definitions

# Search in abbreviations only
teddi search-term "QoS" --scope abbreviations

# Filter by technical bodies
teddi search-term "test" --technical-bodies "3gpp,etsi"

# Output formats
teddi search-term "QoS" --output table
teddi search-term "QoS" --output json
teddi search-term "QoS" --output ison
teddi search-term "QoS" --output toon
```

### List Technical Bodies

```bash
teddi list-bodies
# or
teddi-cli list-bodies
```

### MCP Server

```bash
# Start the MCP server (stdio mode)
teddi-mcp
```

## Output Formats

| Format | Description |
|--------|-------------|
| `table` | Human-readable table (default) |
| `json` | Standard JSON |
| `ison` | Token-optimized format |
| `toon` | Tree-style token-optimized format |

## MCP Integration

Configure your AI agent client:

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

### Available MCP Tools

- `search_term` - Search for terms in TEDDI
- `list_technical_bodies` - List available technical bodies
- `fetch_document` - Retrieve document content
