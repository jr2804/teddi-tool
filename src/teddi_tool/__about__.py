"""Version information for TEDDI Tool."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

__title__ = "teddi_tool"
__description__ = "CLI and FastMCP server for the ETSI TEDDI terminology database"
__author__ = "Jan Reimes"
__email__ = "jan.reimes@head-acoustics.com"
__license__ = "MIT"
__copyright__ = "Copyright 2026, Jan Reimes"

try:
    __version__ = version("teddi-tool")
except PackageNotFoundError:  # pragma: no cover - installed packages always have metadata
    __version__ = "0.0.0"  # Fallback for development mode
