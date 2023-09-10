import inspect
from collections.abc import Awaitable
from typing import Any, Callable


async def load(function_or_value: Awaitable | Callable | Any) -> Any:
    """Load given function or value.

    If value, return it.
    If function, run it and return
    If awaitable (corotine), await it and return

    Args:
        function_or_value: function or value

    Returns: loaded value
    """
    if inspect.iscoroutine(function_or_value):
        return await function_or_value
    elif callable(function_or_value):
        return function_or_value()
    return function_or_value


def discard_value(function_or_value: Awaitable | Callable | Any) -> None:
    if inspect.iscoroutine(function_or_value):
        function_or_value.close()
