---
name: teddi
description: Use when searching the ETSI TEDDI terminology database for terms, abbreviations, or definitions, when listing or validating technical body filters, or when querying TEDDI through the teddi-tool CLI or its FastMCP server.
---

# TEDDI: terms and definitions search

## Overview

TEDDI (Terms and Definitions Database Interactive) holds definitions and
abbreviations extracted from publicly available ETSI deliverables. The same
term often has several entries, differing by spelling variant, scope, or
technical body, so results must be compared rather than collapsed.

`teddi-tool` exposes the same search core through two interfaces:

| Need | Interface | Entry point |
| --- | --- | --- |
| Terminal, scripts, pipes | Cyclopts CLI | `teddi-tool` (alias `teddi`, `teddi-cli`) |
| Chat / agent tools | FastMCP server (stdio) | `teddi-mcp` (or `teddi-tool server`) |

## CLI

Install once with `uv tool install teddi-tool`, or run from a checkout with
`uv run teddi-tool`.

```bash
teddi-tool search-term HATS
teddi-tool search-term HATS --scope definitions --pattern exactmatch --output json
teddi-tool list-bodies
teddi-tool server          # MCP server on stdio
```

### Options

| Option | Values | Default |
| --- | --- | --- |
| `--scope`, `-s` | `abbreviations`, `definitions`, `both` | `both` |
| `--pattern`, `-p` | `exactmatch`, `startingwith`, `endingwith`, `alloccurrences` | `alloccurrences` |
| `--technical-bodies`, `-t` | comma-separated codes from `list-bodies` | unset (all) |
| `--output`, `-o` | `table`, `json`, `ison`, `toon` | `table` |

Every option also reads an environment variable: `TEDDI_TOOL_SCOPE`,
`TEDDI_TOOL_PATTERN`, `TEDDI_TOOL_TECHNICAL_BODIES`, `TEDDI_TOOL_OUTPUT`.

Use `json` for downstream parsing, `ison`/`toon` for compact model-readable
output, and `table` for humans.

## MCP server

Register the installed server with any MCP client:

```json
{
  "mcpServers": {
    "teddi-tool": {
      "command": "uvx",
      "args": ["--from", "teddi-tool", "teddi-mcp"]
    }
  }
}
```

Inside a checkout use `"command": "uv", "args": ["run", "teddi-mcp"]`.

Clients may prefix tool names with the server name, for example
`mcp_teddi-tool_search_teddi`.

### `search_teddi`

Arguments: `term` (required), `search_in` (`abbreviations`, `definitions`, or
`both`, default `both`), `search_pattern` (`exactmatch`, `startingwith`,
`endingwith`, or `alloccurrences`, default `alloccurrences`), and optional
`technical_bodies`.

Returns an object with `query` (the normalized request), `total_count`, and
`results[]`, where each result has `term`, `description`, and `documents[]`
with `technical_body`, `specification`, and `url`.

### `get_term_info`

Arguments: `term` (required) and optional `technical_bodies`. It forces
`search_in="both"` and `search_pattern="exactmatch"` and adds an
`exact_match` boolean to the payload.

### `list_technical_bodies`

No arguments. Returns `{"technical_bodies": [...]}` with the codes accepted by
`technical_bodies` (the TEDDI search form advertises 115, such as `3GPP`,
`Ecma`, `eHEALTH`, `STQ`). Filters are matched case-insensitively, and `all`
searches every body.

## Recommended workflow

1. Discover valid filters with `list-bodies` / `list_technical_bodies`.
2. Search with explicit scope and pattern (`both` plus `exactmatch` for strict
   lookups).
3. Filter by technical body only with codes returned in step 1.
4. Use `get_term_info` when one specific entry is wanted.
5. Summarize: one-line meaning, body-specific differences, and source
   specifications or URLs where available.

## Interpretation guidance

- Keep distinct definitions distinct when wording or scope differs.
- Call out singular/plural variants such as "Simulator" vs "Simulators".
- Say explicitly when a requested body or filter has no match.
- If a search returns nothing, retry with different casing (`HATS` vs `hats`)
  and then with `alloccurrences`; keep the body filter unless asked to broaden.

## Troubleshooting

- Invalid option value: use only the values listed above; enums are the
  contract, not free-form strings.
- Invalid technical body: run `list-bodies` and reuse returned codes exactly.
- Empty `list-bodies` result means no body codes are configured yet, not a
  failed request.
- Network or TLS errors: the client caches responses in
  `.cache/teddi_http.sqlite3`; retry after the upstream site recovers.
