import time as tm

from async_cache import CacheFunc


async def test_decorator_async():
    class GlobalCount:
        called = 0

    @CacheFunc()
    async def test():
        GlobalCount.called = GlobalCount.called + 1
        return GlobalCount.called

    result_1 = await test()
    assert result_1 == 1

    tm.sleep(0.2)

    result_2 = await test()
    assert result_2 == 1

    assert id(result_1) == id(result_2)


async def test_decorator_async_ttl():
    class GlobalCount:
        called = 0

    @CacheFunc(ttl=0.1)
    async def test():
        GlobalCount.called = GlobalCount.called + 1
        return GlobalCount.called

    result_1 = await test()
    assert result_1 == 1

    tm.sleep(0.2)

    result_2 = await test()
    assert result_2 == 2

    assert id(result_1) != id(result_2)


async def test_decorator_sync():
    class GlobalCount:
        called = 0

    @CacheFunc()
    def test():
        GlobalCount.called = GlobalCount.called + 1
        return GlobalCount.called

    result_1 = await test()
    assert result_1 == 1

    tm.sleep(0.2)

    result_2 = await test()
    assert result_2 == 1

    assert id(result_1) == id(result_2)


async def test_decorator_sync_ttl():
    class GlobalCount:
        called = 0

    @CacheFunc(ttl=0.1)
    def test():
        GlobalCount.called = GlobalCount.called + 1
        return GlobalCount.called

    result_1 = await test()
    assert result_1 == 1

    tm.sleep(0.2)

    result_2 = await test()
    assert result_2 == 2

    assert id(result_1) != id(result_2)
