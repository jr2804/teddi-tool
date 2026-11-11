"""Cyclopts CLI app for TEDDI Tool."""

from __future__ import annotations

from cyclopts import App

from teddi_tool.__about__ import __version__
from teddi_tool.cli import commands

app = App(
    name="teddi-tool",
    help="Search the ETSI TEDDI terminology database or run its MCP server",
    version=__version__,
    version_flags=["--version", "-V"],
)


def _default() -> None:
    """Show the application help."""
    app.help_print()


app.command(commands.search_term, name="search-term")
app.command(commands.list_bodies, name="list-bodies")
app.command(commands.server, name="server")
app.default(_default)

app.register_install_completion_command()


def main() -> None:
    """Entry point for the CLI application."""
    app()
