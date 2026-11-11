"""Tests for the FastMCP server module."""

import pytest

from src.teddi_tool.server import _ttl_from_env


class TestTtlFromEnv:
    """Test environment-variable TTL parsing."""

    def test_missing_env_uses_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test unset or blank variables fall back to the default."""
        monkeypatch.delenv("TEDDI_TOOL_CACHE_TTL", raising=False)
        monkeypatch.setenv("TEDDI_TOOL_MENU_CACHE_TTL", "  ")
        assert _ttl_from_env("TEDDI_TOOL_CACHE_TTL", 7200) == 7200
        assert _ttl_from_env("TEDDI_TOOL_MENU_CACHE_TTL", 90) == 90

    def test_env_overrides_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test a valid environment value wins over the default."""
        monkeypatch.setenv("TEDDI_TOOL_CACHE_TTL", "60")
        assert _ttl_from_env("TEDDI_TOOL_CACHE_TTL", 7200) == 60

    def test_non_positive_env_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test zero or negative values are rejected with a clear error."""
        monkeypatch.setenv("TEDDI_TOOL_CACHE_TTL", "0")
        with pytest.raises(ValueError, match="must be a positive"):
            _ttl_from_env("TEDDI_TOOL_CACHE_TTL", 7200)

    def test_non_numeric_env_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test unparsable values surface the underlying ValueError."""
        monkeypatch.setenv("TEDDI_TOOL_CACHE_TTL", "two hours")
        with pytest.raises(ValueError, match="invalid literal for int"):
            _ttl_from_env("TEDDI_TOOL_CACHE_TTL", 7200)
