---
name: cli-teddi
description: CLI usage for teddi-cli from source in this repository. Use when running TEDDI term searches and listing technical bodies from terminal with uv run commands.
---

# CLI: teddi-cli

## Overview

Use `teddi-cli` for scripted or terminal-based TEDDI operations:

- search terms and definitions,
- list available technical bodies.

Note: `teddi-cli` is search-only. Start server mode with `teddi-mcp` (or `teddi server`).

All commands in this file must be run through uv.

## Commands

### Search a term

```bash
uv run teddi-cli term HATS
```

### Search with filters

```bash
uv run teddi-cli term HATS \
  --scope both \
  --pattern exactmatch \
  --technical-bodies 3gpp,itu,stq
```

### List technical bodies

```bash
uv run teddi-cli list-bodies
```

### Machine-readable output

```bash
uv run teddi-cli term HATS --output <format>
```

Supported `<format>` values: `table`, `json`, `ison`, `toon`.

## Arguments Reference

- Search scope: `--scope` = `abbreviations` | `definitions` | `both`
- Match behavior: `--pattern` = `exactmatch` | `startingwith` | `endingwith` | `alloccurrences`
- Body filter: `--technical-bodies` = comma-separated codes such as `3gpp,stq`
- Output format: `--output` = `table` | `json` | `ison` | `toon`

Common combinations:

- Broad search: `--scope both --pattern alloccurrences`
- Strict search: `--scope both --pattern exactmatch`
- Filtered JSON: `--scope both --pattern exactmatch --technical-bodies 3gpp,stq --output json`

## Troubleshooting

If a technical body is reported unknown:

1. Run `list-bodies` and use returned codes exactly.
2. Retry with normalized lowercase codes.

If exact match returns no rows:

1. Retry using uppercase term.
2. Retry with `--pattern alloccurrences`.
