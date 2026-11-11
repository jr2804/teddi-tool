# Usage

## Executables

| Executable | Description |
|------------|-------------|
| `teddi-tool` | Full CLI: `search-term`, `list-bodies`, `server` |
| `teddi` | Alias of `teddi-tool` |
| `teddi-cli` | Alias of `teddi-tool` (kept for existing scripts) |
| `teddi-mcp` | MCP server only (stdio) |

`teddi server` and `teddi-mcp` are equivalent. Shell completion is installed with
`teddi-tool --install-completion`.

## CLI Commands

### Search Terms

```bash
teddi search-term "QoS"                        # table output (default)
teddi search-term "QoS" --pattern exactmatch
teddi search-term "QoS" --pattern startingwith
teddi search-term "QoS" --pattern endingwith
teddi search-term "QoS" --scope definitions
teddi search-term "QoS" --scope abbreviations
teddi search-term "test" --technical-bodies "3gpp,stq"
teddi search-term "QoS" --output json
teddi search-term "QoS" --output ison
teddi search-term "QoS" --output toon
```

| Option | Values | Environment variable |
|--------|--------|----------------------|
| `--scope`, `-s` | `abbreviations`, `definitions`, `both` (default) | `TEDDI_TOOL_SCOPE` |
| `--pattern`, `-p` | `alloccurrences` (default), `exactmatch`, `startingwith`, `endingwith` | `TEDDI_TOOL_PATTERN` |
| `--technical-bodies`, `-t` | Comma-separated codes, case-insensitive; `all` clears the filter | `TEDDI_TOOL_TECHNICAL_BODIES` |
| `--output`, `-o` | `table` (default), `json`, `ison`, `toon` | `TEDDI_TOOL_OUTPUT` |

Exact-match searches are useful for abbreviations; `alloccurrences` also matches
longer definitions that contain the term.

### List Technical Bodies

```bash
teddi list-bodies
```

Prints the 115 codes advertised by the TEDDI search form, for example:

```text
Available Technical Bodies:
  - 3GPP
  - AERO
  - AFI
  ...
  - STQ
```

Values are matched case-insensitively on input (`stq`, `STQ` and `Stq` are the
same filter) but sent to TEDDI with their published casing.

### MCP Server

```bash
teddi-mcp            # or: teddi server
```

## Output Formats

| Format | Description |
|--------|-------------|
| `table` | Human-readable rich table with term, description, TB and specification (default) |
| `json` | Indented JSON payload for scripts |
| `ison` | Compact ISON encoding of the same payload |
| `toon` | Token-oriented TOON encoding for LLM prompts |

Machine-readable formats share one payload shape:

```json
{
  "query": {
    "term": "QoS",
    "search_in": "both",
    "search_pattern": "exactmatch",
    "technical_bodies": ["STQ"]
  },
  "total_count": 2,
  "results": [
    {
      "term": "QoS",
      "description": "Quality of Service",
      "documents": [
        {
          "technical_body": "STQ",
          "specification": "TS 102 894-2",
          "url": "https://webapp.etsi.org/..."
        }
      ]
    }
  ]
}
```

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

| Tool | Arguments | Returns |
|------|-----------|---------|
| `search_teddi` | `term`, `search_in`, `search_pattern`, `technical_bodies` | Payload with `query`, `total_count` and `results` |
| `get_term_info` | `term`, `technical_bodies` | Exact-match payload plus an `exact_match` boolean |
| `list_technical_bodies` | none | `{"technical_bodies": [...]}` |

`search_in` and `search_pattern` use the same values as the CLI. `technical_bodies`
is a comma-separated string, so agents do not have to send arrays.

`fetch_document()` exists on the client but is intentionally not exposed as an MCP
tool or CLI command.

## Caching

Successful TEDDI responses are cached in `.cache/teddi_http.sqlite3` with a
two-hour TTL. Delete that file (or pass a different `cache_dir` to the client) to
force fresh requests. Failed responses are not cached; they surface as
`httpx2.HTTPError`.

## Troubleshooting

- **`Invalid technical body 'xyz'`** — the filter contains a code TEDDI does not
  publish. Run `teddi list-bodies`; the error message lists all valid values.
- **No results** — try `--pattern alloccurrences` (the default) or widen
  `--scope` to `both`; TEDDI only searches the term, not document text.
- **Empty `list-bodies` output** — the menu page could not be fetched or parsed;
  the client falls back to its bundled code list, so an empty result indicates a
  broken installation rather than missing data.
