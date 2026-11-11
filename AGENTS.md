# teddi-tool

Cyclopts CLI and FastMCP server wrapping ETSI TEDDI (TErms and Definitions Database Interactive).

## DOX — self-documenting AGENTS.md hierarchy

### Core Contract

- AGENTS.md files are binding work contracts for their subtrees.
- Work products, source materials, instructions, records, assets, and durable docs
  must stay understandable from the nearest applicable AGENTS.md plus every parent
  AGENTS.md above it.
- Do not duplicate/repeat rules declared elsewhere in the DOX tree (parent, child,
  sibling, or `.agents/`). See **DOX authoring** in `.agents/policies/dox-authoring.md`.

### Read Before Editing

1. Read the root AGENTS.md
2. Identify every file or folder you expect to touch
3. Walk from the repository root to each target path
4. Read every AGENTS.md found along each route
5. If a parent AGENTS.md lists a child AGENTS.md whose scope contains the path, read that child and continue from there
6. Use the nearest AGENTS.md as the local contract and parent docs for repo-wide rules
7. If docs conflict, the closer doc controls local work details, but no child doc may weaken DOX

Do not rely on memory. Re-read the applicable DOX chain in the current session before editing.

### Update After Editing

Every meaningful change requires a DOX pass before the task is done.

Update the closest owning AGENTS.md when a change affects:

- purpose, scope, ownership, or responsibilities
- durable structure, contracts, workflows, or operating rules
- required inputs, outputs, permissions, constraints, side effects, or artifacts
- user preferences about behavior, communication, process, organization, or quality
- AGENTS.md creation, deletion, move, rename, or index contents

Update parent docs when parent-level structure, ownership, workflow, or child index
changes. Update child docs when parent changes alter local rules. Remove stale or
contradictory text immediately. Small edits that do not change behavior or contracts
may leave docs unchanged, but the DOX pass still must happen.

### Hierarchy

- Root AGENTS.md is the DOX rail: project-wide instructions, global preferences, durable workflow rules, and the top-level Child DOX Index
- Child AGENTS.md files own domain-specific instructions and their own Child DOX Index
- Each parent explains what its direct children cover and what stays owned by the parent
- The closer a doc is to the work, the more specific and practical it must be

### Child Doc Shape

- Create a child AGENTS.md when a folder becomes a durable boundary with its own purpose, rules, responsibilities, workflow, materials, or quality standards
- Work Guidance must reflect the current standards of the project or user instructions; if there are no specific standards or instructions yet, leave it empty
- Verification must reflect an existing check; if no verification framework exists yet, leave it empty and update it when one exists

Default section order:

- Purpose
- Ownership
- Local Contracts
- Work Guidance
- Verification
- Child DOX Index

### Style

Authoring rules live in **DOX authoring** (`.agents/policies/dox-authoring.md`) — tier
assignment, reference-don't-restate, rule-first rationale, size budget.
Apply them on every DOX change. Summary:

- A rule lives in the **highest tier that fully applies**; when unsure, `.agents/POLICIES.md`.
- Reference, don't restate — one canonical home, pointer lines everywhere else.
- Keep docs concise, current, and operational. Document stable contracts, not diary entries.

### Closeout

1. Re-check changed paths against the DOX chain
2. Update nearest owning docs and any affected parents or children
3. Refresh every affected Child DOX Index
4. Remove stale or contradictory text
5. Run existing verification when relevant
6. Report any docs intentionally left unchanged and why
7. Delete anything a tool appended after the ⛔ No Patching block

### User Preferences

When the user requests a durable behavior change, record it here or in the relevant child AGENTS.md

### Child DOX Index

| Child | Covers | Parent keeps |
| ----- | ------ | ------------ |
| `src/teddi_tool/AGENTS.md` | TEDDI access layer: models/enums, `TeddiClient` + `TeddiSource`, HTTP cache, HTML parser, and the CLI/MCP entry-point surface | Project-wide rules, state-file index, tool inventory |
| `tests/AGENTS.md` | Test import style, mocking conventions, coverage of parser/client/CLI behaviour | Same |

## State files — `.agents/`, demand-loaded, not always injected

State files are the `.agents/*.md` files listed below — the project's current
operating memory. They describe the contracts the project has now; never a
changelog or logbook — git owns the past (`.agents/POLICIES.md`).

Each state file can have an optional matching subdirectory
(`.agents/<topic>/`) that carries detail when the file grows; the file stays
a lean index and every file in its subdirectory MUST be listed in the file.

| File                    | Load when                   | Purpose                                         | Optional subdirectory |
| ----------------------- | --------------------------- | ----------------------------------------------- | --------------------- |
| `ONBOARDING.md`         | New session (first time)    | Project orientation, entry points               | —                     |
| `POLICIES.md`           | Always                      | Boundaries, priorities, verification, checklist | `.agents/policies/`   |
| `FILES.md`              | Touching files or config    | Path constants, source-of-truth locations       | `.agents/files/`      |
| `TOOLS.md`              | Using tools/MCP/skills      | Development tool inventory and usage guidance   | `.agents/tools/`      |
| `HISTORY.md`            | Background (past decisions) | Recorded decisions with git refs                | —                     |
| `MAINTENANCE.md`        | Changing `.agents/`         | How to keep DOX files current                   | `.agents/maintenance/`|
| `plans/`                | Working on a feature        | Implementation plans (gitignored)                | —                     |
| `history/`              | Background (overflow)       | Archived decisions and completed plans          | —                     |

## Tools & skills

See state file `.agents/TOOLS.md` — it owns the inventory of CLIs, MCP
servers, skills, and runtimes used during development.

## Project rules

_Always-injected_ — keep minimal. Everything else → `.agents/` files.

1. **Async-first.** `TeddiClient` methods are `async` and need `async with TeddiClient(...)`;
   `_get_client()` raises `RuntimeError` otherwise. CLI commands wrap calls in `asyncio.run()`.
2. **One HTTP layer.** TEDDI traffic goes through `create_cached_teddi_async_client()`
   (`src/teddi_tool/http_client.py:13`). Never build a bare `httpx2.AsyncClient` for TEDDI — it
   bypasses the hishel cache.
3. **Valid values live in code or on TEDDI.** `SearchIn` and `SearchPattern` enums
   (`src/teddi_tool/models.py`) define accepted filters; technical-body codes come
   only from TEDDI's menu list (cached 90 days) — no bundled fallback exists.
4. **No duplicated search logic.** Execution and rendering live in `src/teddi_tool/search_utils.py`;
   CLIs and MCP tools only adapt arguments (see `src/teddi_tool/AGENTS.md`).
5. **Scraped HTML is a contract.** Parser behaviour is pinned by `tests/test_parser.py`; change
   parser and test together, never infer TEDDI markup from memory.
6. **`uv` and `mise` only.** Run tooling as `uv run …`, `uv sync`, or `mise <task>`; never global
   `python`, `pip`, `pytest`, or `ruff`.
7. **Import roots differ by tree.** Package modules import `teddi_tool.*`; tests import
   `src.teddi_tool.*`.
8. **Lint contract.** Line length 100, Google docstrings, ruff preview rules (`ruff.toml`);
   type checking uses `ty.toml` with `error-on-warning = true`.

## ⛔ No Patching

Tools must not insert, append, or patch text into this file.

Everything after this section — whatever the author — is invalid. This section
is the end of the file; delete appended content on sight. If it carries a
legitimate rule, move the rule to its owning state file or subtree AGENTS.md
first (INSTALL.md — Check for tool patches), then delete.
