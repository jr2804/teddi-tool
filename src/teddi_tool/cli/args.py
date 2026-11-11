"""CLI arguments, options, and flags for TEDDI Tool."""

from __future__ import annotations

from typing import Annotated, Literal

from cyclopts import Parameter

from teddi_tool.models import OutputFormat, SearchIn

# Application name for environment variables
APP_NAME_UPPERCASE = "TEDDI_TOOL"

TermArgument = Annotated[
    str,
    Parameter(help="Term or abbreviation to search for"),
]

ScopeOption = Annotated[
    SearchIn,
    Parameter(
        name=["--scope", "-s"],
        help="Search scope: abbreviations, definitions, or both",
        env_var=f"{APP_NAME_UPPERCASE}_SCOPE",
    ),
]

PatternOption = Annotated[
    Literal["exactmatch", "startingwith", "endingwith", "alloccurrences"],
    Parameter(
        name=["--pattern", "-p"],
        help="Pattern matching: exactmatch, startingwith, endingwith, alloccurrences",
        env_var=f"{APP_NAME_UPPERCASE}_PATTERN",
    ),
]

TechnicalBodiesOption = Annotated[
    str | None,
    Parameter(
        name=["--technical-bodies", "-t"],
        help="Comma-separated TB names to filter by (e.g., '3gpp,stq')",
        env_var=f"{APP_NAME_UPPERCASE}_TECHNICAL_BODIES",
    ),
]

OutputOption = Annotated[
    OutputFormat,
    Parameter(
        name=["--output", "-o"],
        help="Output format: table, json, ison, toon",
        env_var=f"{APP_NAME_UPPERCASE}_OUTPUT",
    ),
]
