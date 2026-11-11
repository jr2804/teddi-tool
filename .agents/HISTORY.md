# AGENTS.md — HISTORY

State file. The one file that may reference the past — sparingly. Read when
relevant to the current task; long-term memory for decisions, not a log.
Routine history lives in git; only record what is costly to rediscover.

## Format

| Date | Decision | Rationale | Git ref |
| ---- | -------- | --------- | ------- |
| YYYY-MM-DD | [description] | [why] | [commit hash/tag] |

## Record

- High-level architectural decisions and breaking changes.
- Dependency, tooling, and platform choices — including the alternative that lost.
- False turns and rejected approaches, with the reason.
- Completion of an implementation plan (link to its archive below).

## Do not record

- Routine commits, refactor logs, session activity, release notes.
- Anything obvious from git, the code, or current AGENTS.md/state files.

## Guidance

- Keep entries brief — enough to reconstruct the reasoning.
- Link to the relevant commits or tags.
- If this file grows large, move older entries to `.agents/history/` and keep
  a pointer here.
- Completed implementation plans are archived as single files at
  `.agents/history/<YYYY-MM-DD-plan-name>.md` and linked from the decision
  entry they belong to. The trigger to archive is **plan completion**, not
  file growth — see `.agents/policies/plans-and-docs.md`.

## Decisions

| Date | Decision | Rationale | Git ref |
| ---- | -------- | --------- | ------- |
| 2026-03-19 | Repository split out of `tdoc-crawler` into a standalone `teddi-mcp` package | TEDDI lookup had no dependency on the 3GPP tdoc crawler; separate release and packaging | `08a2984` |
| 2026-03-20 | Lint and type-check config moved out of `pyproject.toml` into `ruff.toml` and `ty.toml` | Dedicated tool config files keep `pyproject.toml` about packaging; `ty.toml` enables `error-on-warning` | `3075a71` |
| 2026-03-20 | Task/tool config consolidated under `.config/mise/` with per-topic `conf.d/*.toml` | One task runner (`mise`) for format, lint, quality, skills, MCP registration instead of ad-hoc scripts | `d0a0208` |
| 2026-11-10 | Adopted the agents-scaffold DOX hierarchy; root `AGENTS.md` reduced to rail + state-file index | Old `AGENTS.md` was a 96-line design document injected on every call; content moved into `.agents/` and `src/teddi_tool/AGENTS.md` | uncommitted at adoption |
| 2026-11-10 | Dropped `refresh_ttl_on_access` from `create_cached_teddi_async_client`; hishel 2.x TTL is fixed at write time | The keyword no longer exists in `hishel.AsyncSqliteStorage` (it raised `TypeError` on every cache-backed client), and 2.x exposes no refresh-on-access API | uncommitted |
| 2026-11-11 | Renamed distribution/package to `teddi-tool` / `teddi_tool` and adopted the copier-uv-plus template (Cyclopts CLI, Zensical docs, GitHub Actions, tag versioning) | The project is a CLI as well as an MCP server; `teddi-mcp` misrepresented it. `teddi-tool` and the other candidate names are free on PyPI; `teddi` is taken | see migration commits |

## Archived plans

None yet. Completed plans land in `.agents/history/<YYYY-MM-DD-plan-name>.md`.

## Archive a plan

Procedure, naming, and the completion trigger — see
`.agents/policies/plans-and-docs.md` → Archive a plan.
