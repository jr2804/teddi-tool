# Usage

## CLI Commands

### Search Terms

```bash
# Basic search
teddi-mcp search term "QoS"

# Exact match
teddi-mcp search term "QoS" --search-pattern exactmatch

# Starting with
teddi-mcp search term "QoS" --search-pattern startingwith

# Search in definitions only
teddi-mcp search term "QoS" --search-in definitions

# Search in abbreviations only
teddi-mcp search term "QoS" --search-in abbreviations

# Filter by technical bodies
teddi-mcp search term "test" --technical-bodies "3gpp,etsi"

# Output formats
teddi-mcp search term "QoS" --output table
teddi-mcp search term "QoS" --output json
teddi-mcp search term "QoS" --output ison
teddi-mcp search term "QoS" --output toon
```

### List Technical Bodies

```bash
teddi-mcp search list-bodies
```

### MCP Server

```bash
# Start the MCP server (stdio mode)
teddi-mcp server
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
