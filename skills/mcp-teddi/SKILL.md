---
name: mcp-teddi
description: MCP usage for ETSI TEDDI (Terms and Definitions Database Interactive) through the teddi-mcp server. Use when querying terms/abbreviations, listing technical bodies, validating technical body codes, or retrieving exact term definitions from Copilot chat tools.
---

# MCP Server: TEDDI

## Overview

TEDDI (Terms and Definitions Database Interactive) contains definitions and abbreviations extracted from publicly available ETSI deliverables.

Important behavior:

- The same term can have multiple definitions.
- Differences can be minor spelling variants or technical-body specific meanings.
- Technical body filters can change results significantly.

## Tooling

Use these teddi MCP tools:

- `search_teddi`
- `get_term_info`
- `list_technical_bodies`

Depending on the MCP client, tool names may be displayed with a server prefix (for example, `mcp_teddi-mcp_search_teddi`).

## Tool Details

### `list_technical_bodies`

- Purpose: return supported values for `technical_bodies` filtering.
- Arguments: none.
- Returns: object with `technical_bodies` list.

### `search_teddi`

- Purpose: general TEDDI search with explicit scope/pattern controls.
- Arguments:
  - `term` (required string)
  - `search_in` (optional string): `abbreviations` | `definitions` | `both` (default `both`)
  - `search_pattern` (optional string): `exactmatch` | `startingwith` | `endingwith` | `alloccurrences` (default `alloccurrences`)
  - `technical_bodies` (optional comma-separated string)
- Returns: object with:
  - `query` (normalized request values)
  - `total_count`
  - `results[]` with `term`, `description`, and `documents[]` (`technical_body`, `specification`, `url`)

### `get_term_info`

- Purpose: convenience lookup for exact-match term retrieval.
- Arguments:
  - `term` (required string)
  - `technical_bodies` (optional comma-separated string)
- Behavior: internally uses `search_in="both"` and `search_pattern="exactmatch"`.
- Returns: same structure as `search_teddi`, plus `exact_match` boolean.

## Recommended Workflow

1. Step 1: Validate or discover technical body codes with `list_technical_bodies`.
2. Step 2: Run `search_teddi` with explicit `search_in` and `search_pattern`.
3. Step 3: Apply `technical_bodies` filtering only with known valid codes.
4. Step 4: If the user wants one specific entry, use `get_term_info` for exact lookup.
5. Step 5: Summarize results with:
   - concise definition,
   - body-specific differences,
   - document references (spec + URL) when available.

## Query Patterns

### General term exploration

Use `search_teddi` with:

- `search_in="both"`
- `search_pattern="exactmatch"` for strict matching
- `search_pattern="alloccurrences"` when exact match returns nothing

### Technical-body constrained search

Use comma-separated body codes from `list_technical_bodies`, for example:

- `technical_bodies="all"`

If a code is rejected, call `list_technical_bodies` and retry with valid codes.

## Interpretation Guidance

When multiple results are returned:

- Do not collapse distinct definitions into one if wording or scope differs.
- Highlight whether definitions are singular/plural variants (for example, "Simulator" vs "Simulators").
- Mention when a requested body has no match.

When no results are returned:

- If no results are returned for a query, retry with different casing (for example, `HATS` vs `hats`).
- Retry with `alloccurrences`.
- Keep the same technical body filter unless the user asks to broaden scope.

## Output Quality

For explanations, include:

1. A one-line plain-language meaning.
2. Context of use (for example, telecom testing, standards terminology).
3. Differences by technical body.
4. Optional references to source specs from TEDDI response data.
