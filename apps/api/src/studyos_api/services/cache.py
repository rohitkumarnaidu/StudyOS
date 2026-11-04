"""Redis caching layer for StudyOS API."""

from typing import Any

import structlog

logger = structlog.get_logger(__name__)

_client: Any = None
_enabled = False
_local_cache: dict[str, Any] = {}


def init_cache(url: str | None = None) -> None:
    """Initialize Redis connection. Falls back to in-memory dict if unavailable."""
    global _client, _enabled
    if not url:
        _enabled = False
        logger.info("cache.disabled", reason="no Redis URL configured")
        return
    try:
        import asyncio

        import redis.asyncio as redis  # type: ignore[import-not-found]

        _client = redis.from_url(url, decode_responses=True)
        # Verify connection actually works (from_url is lazy)
        asyncio.get_event_loop().run_until_complete(_client.ping())
        _enabled = True
        logger.info("cache.redis.connected", url=url)
    except ImportError:
        _enabled = False
        logger.warning("cache.redis.import_error", hint="pip install redis")
    except Exception as e:
        _enabled = False
        _client = None
        logger.warning("cache.redis.connection_error", error=str(e))


async def get(key: str) -> Any | None:
    """Get cached value by key."""
    if _enabled and _client:
        try:
            return await _client.get(key)
        except Exception as e:
            logger.warning("cache.get.failed", key=key, error=str(e))
            return _local_cache.get(key)
    return _local_cache.get(key)


async def set(key: str, value: Any, ttl: int = 300) -> None:
    """Set cached value with TTL (seconds)."""
    if _enabled and _client:
        try:
            await _client.setex(key, ttl, value)
        except Exception as e:
            logger.warning("cache.set.failed", key=key, error=str(e))
            _local_cache[key] = value
    else:
        _local_cache[key] = value


async def delete(key: str) -> None:
    """Delete cached value."""
    if _enabled and _client:
        try:
            await _client.delete(key)
        except Exception as e:
            logger.warning("cache.delete.failed", key=key, error=str(e))
    _local_cache.pop(key, None)


async def invalidate_pattern(pattern: str) -> None:
    """Invalidate all keys matching pattern."""
    if _enabled and _client:
        try:
            async for key in _client.scan_iter(match=pattern):
                await _client.delete(key)
        except Exception as e:
            logger.warning("cache.invalidate.failed", pattern=pattern, error=str(e))
    else:
        keys_to_delete = [k for k in _local_cache if k.startswith(pattern)]
        for k in keys_to_delete:
            del _local_cache[k]


def cache_key(*parts: str) -> str:
    """Build cache key from parts."""
    return "studyos:" + ":".join(str(p) for p in parts if p)
