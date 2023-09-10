import asyncio
from unittest.mock import AsyncMock

from async_cache import Cache


async def test_key_value_and_get_direct_value():
    cache = Cache()

    stored_value = await cache.key_value("key", "123")
    assert stored_value == "123"


async def test_key_value_and_get_callable():
    def get_value():
        return 1

    cache = Cache()

    stored_value = await cache.key_value("key", get_value)
    assert stored_value == 1


async def test_key_value_and_get_awaitable():
    async def get_value():
        return 1

    cache = Cache()

    stored_value = await cache.key_value("key", get_value())
    assert stored_value == 1


async def test_key_value_duplicated_within_eol():
    cache = Cache(max_size=1)

    assert await cache.key_value("key", "123") == "123"
    assert await cache.key_value("key", "456") == "123"


async def test_key_value_duplicated_forced():
    cache = Cache(max_size=1)

    assert await cache.key_value("key", "123") == "123"
    assert await cache.key_value("key", "456", force=True) == "456"


async def test_key_value_duplicated_async():
    cache = Cache(max_size=1)

    func = AsyncMock(return_value="loaded_value")
    corotine = func()
    assert await cache.key_value("key", corotine) == "loaded_value"
    assert await cache.key_value("key", corotine) == "loaded_value"

    func.assert_called_once()


async def test_key_value_outdated_entry():
    cache = Cache(max_size=1, ttl=0.1)

    assert await cache.key_value("key", 1) == 1
    await asyncio.sleep(0.01)  # not outdated yet
    assert await cache.key_value("key", 2) == 1

    await asyncio.sleep(0.2)
    assert await cache.key_value("key", 2) == 2
