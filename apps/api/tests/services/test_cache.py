"""Tests for Redis cache layer."""

import pytest

from studyos_api.services import cache


@pytest.fixture(autouse=True)
def reset_cache() -> None:
    """Reset cache state before each test."""
    cache._local_cache.clear()
    cache._enabled = False
    cache._client = None


class TestCacheKey:
    def test_single_part(self) -> None:
        assert cache.cache_key("users") == "studyos:users"

    def test_multiple_parts(self) -> None:
        assert cache.cache_key("users", "123", "profile") == "studyos:users:123:profile"

    def test_empty_parts_ignored(self) -> None:
        assert cache.cache_key("users", "", "123") == "studyos:users:123"


class TestCacheSetGet:
    @pytest.mark.asyncio
    async def test_set_and_get(self) -> None:
        await cache.set("key1", "value1")
        result = await cache.get("key1")
        assert result == "value1"

    @pytest.mark.asyncio
    async def test_get_nonexistent(self) -> None:
        result = await cache.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_with_ttl(self) -> None:
        await cache.set("key2", {"nested": True}, ttl=600)
        result = await cache.get("key2")
        assert result == {"nested": True}


class TestCacheDelete:
    @pytest.mark.asyncio
    async def test_delete_existing(self) -> None:
        await cache.set("to_delete", "value")
        await cache.delete("to_delete")
        assert await cache.get("to_delete") is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self) -> None:
        await cache.delete("nonexistent")


class TestCacheInvalidatePattern:
    @pytest.mark.asyncio
    async def test_invalidate_pattern(self) -> None:
        await cache.set("users:1", "u1")
        await cache.set("users:2", "u2")
        await cache.set("posts:1", "p1")
        await cache.invalidate_pattern("users:")
        assert await cache.get("users:1") is None
        assert await cache.get("users:2") is None
        assert await cache.get("posts:1") == "p1"


class TestInitCache:
    def test_init_no_url(self) -> None:
        cache.init_cache(url=None)
        assert cache._enabled is False

    def test_init_empty_url(self) -> None:
        cache.init_cache(url="")
        assert cache._enabled is False
