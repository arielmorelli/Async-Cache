import asyncio
import datetime as dt
from collections import OrderedDict
from collections.abc import Awaitable
from typing import Any, Callable

from async_cache.func import discard_value, load


class CacheEntryNotFound(Exception):
    pass


class _CacheEntry:
    """Represents a cache entry with data and EOL."""

    def __init__(self, data_loaded: Callable | Awaitable | Any, eol: dt.datetime):
        self._data_loader = data_loaded
        self.eol = eol
        self._loaded = asyncio.Event()
        self._data: Any | None = None

    async def load(self) -> Any:
        """Sets value for data"""
        self._data = await load(self._data_loader)
        self._loaded.set()
        return self._data

    async def value(self) -> Any:
        """Get stored value.

        Returns: loaded data
        """
        await self._loaded.wait()
        return self._data


class Cache:  # noqa: WPS214
    """Cache with TTL (time to live) and LRU (least recently used).

    TTL: each entry will stay in the queue for a given time.
    LRU: the key will be moved to the end of the queue every time is accessed.

    This is a process-safe implementation (meant to be used with async).
    ** THIS IS NOT A THREAD SAFE IMPLEMENTATION!! **

    Usage:
        cache = Cache(ttl=30, max_size=1000)  # Creates a cache with maximum 1000 entries with 30 seconds as time to live.

        cache["key"] == "value 1"
        cache["this", "is", "a", "composed", "key"] == "value 2"
        cache["key"]  # output: "value 1"
        cache["this", "is", "a", "composed", "key"]  # output: "value 2"

        sleep(31)  # sleep 1 second more to invalidate all keys
        cache["key"]  # raises KeyError
    """

    def __init__(self, ttl: int | float | None = 30, max_size: int = 1000) -> None:
        """Constructor.

        Args:
            ttl: time to live in seconds. None means no TTL
            max_size: max cache size. Must be bigger than 0
        """
        if max_size < 1:
            raise ValueError("Cache cannot have less than 1 as size.")

        self._cache: OrderedDict = OrderedDict()
        self.ttl = ttl
        self.max_size = max_size

    async def key_value(
        self, key: Any, new_value: Awaitable | Callable | Any, force: bool = False
    ) -> Any:
        """Set a new item, it not present or expired.

        Delete all expired keys.

        Store the value, if not present.
        If the value is callable, it runs the method.
        If the value is a corotine, it awaits the corotine.
        If the value is a raw value, it store direct.

        Args:
            key: cache key.
            new_value: callable, corotine or raw value to be stored.
            force: bool. Overwrite the mehtod, if already present. Methods waiting the older key will not be realoaded with the new value!

        Returns: stored value, if any
        """
        self._delete_expired_keys()

        if force:
            self._cache.pop(key, None)

        cache_entry = self._cache.get(key)
        if cache_entry:
            discard_value(new_value)
            return await cache_entry.value()

        if key not in self._cache and len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)  # delete the first entry

        eol = dt.datetime.now() + dt.timedelta(seconds=self.ttl)
        cache_entry = _CacheEntry(new_value, eol=eol)
        self._cache[key] = cache_entry

        return await cache_entry.load()

    async def get(self, key: Any) -> Any:
        """Set a new item and delete all expired keys.

        Has side-effect or deleting all expired keys

        Args:
            key: cache key.

        Returns: any stored value
        """
        self._delete_expired_keys()

        cached_entry = self._cache.get(key)
        if not cached_entry:
            raise CacheEntryNotFound

        self._cache.move_to_end(key)
        return await cached_entry.value()

    def _delete_expired_keys(self) -> None:
        """Delete all expired keys in dict."""
        keys_to_delete = []
        now = dt.datetime.now()
        for key, cached_entry in self._cache.items():
            if cached_entry.eol > now:
                # Once keys are added ordered by TTL, it can stop once find a key that is not expired
                break
            else:
                keys_to_delete.append(key)
        [self._cache.pop(key, None) for key in keys_to_delete]
