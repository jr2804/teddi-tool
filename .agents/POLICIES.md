# AGENTS.md — POLICIES

Always applicable. Boundaries, priorities, verification, checklist.

Detail files (`.agents/policies/`):

| File | Covers |
| ---- | ------ |
| `dox-authoring.md` | Tiering, reference-don't-restate, content rules, state-file subdirectories, size budget |
| `plans-and-docs.md` | Implementation plans, plan archiving, documentation/history rules |

## Priorities

1. Correctness
2. Evidence
3. Safety
4. Minimal changes
5. Consistency
6. Performance

## Boundaries

- NEVER fabricate paths, commits, APIs, config keys, env vars, test results,
  or benchmark numbers. If you don't know, say so.
- NEVER guess at command names, flags, or paths. Read source or run `--help`.
- NEVER add secrets, API keys, or tokens to files. Use env vars.
- NEVER run destructive commands (`rm -rf`, `git reset --hard`,
  `git push --force`) without explicit confirmation.
- NEVER delete or move files without explicit instruction.
- NEVER create temp files in project root. Use dedicated temp dir.

Project-specific:

- Do not hit the live TEDDI endpoint from tests or automation — mock the
  `httpx` client (see `tests/AGENTS.md`).
- Do not commit `.cache/`, `tests/.cache/`, or `.agents/plans/`.
- TEDDI has no public API contract. Treat the scraped page shape as evidence
  that must be re-checked, never as prior knowledge.

## Change constraints

- Minimal, surgical edits. Preserve existing style.
- No new dependencies without explicit instruction.
- No unrelated refactoring while fixing a bug.
- A model/enum change is a cross-layer change — see `src/teddi_mcp/AGENTS.md`
  → Work Guidance before editing `src/teddi_mcp/models.py`.

## Code quality

Universal defaults. Project-specific standards live in child AGENTS.md.

- **SRP** — one reason to change per module/function.
- **DRY** — check before adding. Extract on third occurrence (Rule of Three).
- **Redundant code** — remove dead branches, unreachable conditions, unused
  params/imports before finishing.
- **Duplication vs. abstraction** — prefer duplication over wrong premature
  abstraction.
- No new code-quality tooling by default — opt in per project.

## Completion checklist

- Change solves the stated problem
- Relevant validation ran (or gaps stated)
- No unintended side effects or secrets exposed

## Verification

Run from the repository root:

```bash
uv run pytest tests/ -v
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run ty check
```

`ty.toml` sets `error-on-warning = true`. Markdown formatting
(`mise run format-md`) is optional and currently has no CI gate.

Gaps as of 2026-11-10: `mise run lint` / `lint-fix*` still target
`corr_plot/ tests/ packages/` (stale paths), and there is no `test` or
`typecheck` mise task. Use the `uv run` commands above.

## Response format

Concise and specific. No filler, intros, or restated requirements.
Answer direct questions directly.

For review/debugging/analysis: findings with references, conclusion,
approach. Mention caveats.
