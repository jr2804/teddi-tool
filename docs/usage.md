# Usage

## Executables

| Executable | Description |
|------------|-------------|
| `teddi-tool` | Full CLI: `search-term`, `list-bodies`, `server` |
| `teddi` | Alias of `teddi-tool` |
| `teddi-cli` | Alias of `teddi-tool` (kept for existing scripts) |
| `teddi-mcp` | MCP server only (stdio) |

`teddi server` and `teddi-mcp` are equivalent. Shell completion is available via
`teddi-tool --install-completion`.

## CLI Commands

### Search Terms

```bash
teddi search-term "QoS"                        # table output (default)
teddi search-term "QoS" --pattern exactmatch
teddi search-term "QoS" --pattern startingwith
teddi search-term "QoS" --scope definitions
teddi search-term "QoS" --scope abbreviations
teddi search-term "test" --technical-bodies "3gpp,stq"
teddi search-term "QoS" --output json
teddi search-term "QoS" --output ison
teddi search-term "QoS" --output toon
```

Options can also be supplied through environment variables:
`TEDDI_TOOL_SCOPE`, `TEDDI_TOOL_PATTERN`, `TEDDI_TOOL_TECHNICAL_BODIES`,
`TEDDI_TOOL_OUTPUT`.

### List Technical Bodies

```bash
teddi list-bodies
```

### MCP Server

```bash
teddi-mcp            # or: teddi server
```

## Output Formats

| Format | Description |
|--------|-------------|
| `table` | Human-readable rich table (default) |
| `json` | Standard JSON |
| `ison` | Token-optimized ISON |
| `toon` | Tree-style token-optimized TOON |

## MCP Integration

```json
{
  "mcpServers": {
    "teddi": {
      "command": "teddi-mcp"
    }
  }
}
```

### Available MCP Tools

- `search_teddi` — search terms with scope, pattern, and TB filters
- `get_term_info` — exact-match entries for one term, plus an `exact_match` flag
- `list_technical_bodies` — supported TB filter values

`fetch_document()` exists on the client but is intentionally not exposed as an
MCP tool.
