"""Shared CLI argument and option definitions."""

from typing import Annotated

import typer

from teddi_mcp.models import OutputFormat, SearchIn, SearchPattern

TermArgument = Annotated[str, typer.Argument(help="Term to search for")]

ScopeOption = Annotated[
    SearchIn,
    typer.Option("--scope", "-s", help="Search scope: abbreviations, definitions, or both"),
]

PatternOption = Annotated[
    SearchPattern,
    typer.Option(
        "--pattern",
        "-p",
        help="Pattern matching: exactmatch, startingwith, endingwith, alloccurrences",
    ),
]

TechnicalBodiesOption = Annotated[
    str | None,
    typer.Option(
        "--technical-bodies",
        "-t",
        help="Comma-separated TB names to filter by (e.g., '3gpp,etsi')",
    ),
]

OutputOption = Annotated[
    OutputFormat,
    typer.Option("--output", "-o", help="Output format: json, ison, toon, table"),
]
