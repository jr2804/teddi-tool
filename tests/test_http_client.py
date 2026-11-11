"""Tests for the cached TEDDI HTTP client factory."""

from pathlib import Path

import httpx2
import pytest
from hishel import AsyncSqliteStorage
from hishel.httpx2 import AsyncCacheClient

from src.teddi_tool.http_client import create_cached_teddi_async_client


class TestCreateCachedTeddiAsyncClient:
    """Verify the hishel-backed client factory builds a usable client."""

    @pytest.mark.asyncio
    async def test_builds_client_with_sqlite_cache(self, tmp_path: Path) -> None:
        """Factory returns a hishel client backed by the TEDDI cache database."""
        cache_dir = tmp_path / ".cache"

        client = await create_cached_teddi_async_client(cache_dir=cache_dir)

        try:
            assert isinstance(client, httpx2.AsyncClient)
            assert isinstance(client, AsyncCacheClient)

            storage = getattr(client, "storage", None)
            assert isinstance(storage, AsyncSqliteStorage)
            assert Path(storage.database_path) == cache_dir / "teddi_http.sqlite3"
            assert client.timeout.read == 30.0
            assert client.headers["User-Agent"].startswith("Mozilla/5.0")
        finally:
            await client.aclose()

        assert cache_dir.is_dir()

    @pytest.mark.asyncio
    async def test_honours_cache_ttl_argument(self, tmp_path: Path) -> None:
        """A non-default TTL is passed through to the storage backend."""
        client = await create_cached_teddi_async_client(
            cache_dir=tmp_path / ".cache",
            cache_ttl=60,
        )

        try:
            storage = getattr(client, "storage", None)
            assert isinstance(storage, AsyncSqliteStorage)
            assert storage.default_ttl == 60
        finally:
            await client.aclose()
