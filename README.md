# Async-Cache

Simple local **async** cache library supporting LRU and TTL.

## Motivation

Created to study/explain how async works in Python.

## Usage


### Decorator

```python
from async_cache import CacheFunc


@CacheFunc()
async def func():
    ...

result_1 = await func()
```



### Direct access
```python
from async_cache import Cache


cache = Cache()
stored_value = await cache.key_value("key", "value")
```
