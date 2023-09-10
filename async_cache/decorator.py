import functools
import inspect
from collections.abc import Awaitable
from typing import Any, Callable

from async_cache import Cache


class CacheFunc:
    def __init__(self, ttl: int | float | None = 30, max_size: int = 1000) -> None:
        """Constructor.

        Args:
            ttl: time to live in seconds. None means no TTL
            max_size: max cache size. Must be bigger than 0
        """
        self.cache = Cache(ttl=ttl, max_size=max_size)

    def __call__(self, func) -> Callable:
        """__call__ implementation.

        Args:
            func: function to be decorated

        Returns: Callable
        """

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            func_value = functools.partial(func, *args, **kwargs)()
            return await self.cache.key_value(args, func_value)

        return wrapper
