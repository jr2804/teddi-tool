"""Generate release notes for a tag with an OpenAI-compatible chat endpoint.

Usage:
    python scripts/release_notes.py --from-tag v1.2.2 --to-ref HEAD

Reads commits with `git log`, asks the model for a short Markdown changelog,
and falls back to a plain commit list when no API key is configured.

Environment:
    OPENAI_API_KEY   required for LLM output; omit to use the fallback
    OPENAI_BASE_URL  default https://api.openai.com/v1
    OPENAI_MODEL     default gpt-4o-mini
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import httpx2

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
MAX_COMMITS = 200
MAX_DIFF_CHARS = 12_000

SYSTEM_PROMPT = (
    "You write release notes for a Python CLI and MCP server project. "
    "Group changes under 'Features', 'Fixes', and 'Other'. Keep each bullet "
    "to one line, start with a verb, and mention user-visible behaviour. "
    "Do not invent changes, do not add a title, and do not wrap the answer "
    "in code fences. Output Markdown only."
)


def main() -> int:
    """Write release notes to stdout (or --output)."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-tag", help="previous tag; defaults to the last reachable tag")
    parser.add_argument("--to-ref", default="HEAD", help="end revision (default: HEAD)")
    parser.add_argument("--output", type=Path, help="write notes to this file instead of stdout")
    args = parser.parse_args()

    from_tag = args.from_tag or _previous_tag(args.to_ref)
    commits = _commits(from_tag, args.to_ref)
    if os.environ.get("OPENAI_API_KEY"):
        notes = _llm_notes(commits, _diff_stat(from_tag, args.to_ref))
    else:
        print("OPENAI_API_KEY not set; using the commit-list fallback.", file=sys.stderr)
        notes = _fallback(commits)

    if args.output:
        args.output.write_text(notes, encoding="utf-8")
    else:
        sys.stdout.buffer.write(notes.encode("utf-8"))
    return 0


def _previous_tag(ref: str) -> str | None:
    """Return the most recent tag reachable from *ref*, if any."""
    try:
        return _git("describe", "--tags", "--abbrev=0", f"{ref}^")
    except subprocess.CalledProcessError:
        return None


def _commits(from_tag: str | None, to_ref: str) -> list[str]:
    """Collect commit subjects between *from_tag* and *to_ref*."""
    revision_range = f"{from_tag}..{to_ref}" if from_tag else to_ref
    log = _git("log", f"--max-count={MAX_COMMITS}", "--pretty=format:%h%x09%s", revision_range)
    return [line for line in log.splitlines() if line.strip()]


def _diff_stat(from_tag: str | None, to_ref: str) -> str:
    """Return a truncated diffstat for context."""
    revision_range = f"{from_tag}..{to_ref}" if from_tag else to_ref
    stat = _git("diff", "--stat", revision_range)
    return stat[:MAX_DIFF_CHARS]


def _git(*args: str) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.strip()


def _fallback(commits: list[str]) -> str:
    """Build a plain Markdown changelog from commit subjects."""
    if not commits:
        return "No changes since the previous release."
    bullets = "\n".join(f"- {line.split(chr(9), 1)[-1]}" for line in commits)
    return f"## Changes\n\n{bullets}\n"


def _llm_notes(commits: list[str], diffstat: str) -> str:
    """Ask an OpenAI-compatible endpoint for release notes."""
    api_key = os.environ["OPENAI_API_KEY"]
    base_url = os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    model = os.environ.get("OPENAI_MODEL", DEFAULT_MODEL)
    user_prompt = (
        "Commits since the previous release:\n" + "\n".join(commits) + "\n\nDiffstat:\n" + diffstat
    )
    response = httpx2.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout=60.0,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return content.strip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
