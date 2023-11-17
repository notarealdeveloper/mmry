import pytest
from mmry import CacheDefault

def foo(s):
    return s.replace('hello', 'goodbye')

def test_cache():

    cache = CacheDefault('test')

    s = 'hello, world'

    # prepare
    cache.delete(s)

    # not have
    assert not cache.have(s)
    with pytest.raises(FileNotFoundError):
        cache.load(s)

    cache.save(s, foo(s))

    # have
    o = cache.load(s)
    assert o.decode() == foo(s)
    assert cache.have(s)

    # delete
    assert cache.delete(s)

    # not have
    assert not cache.have(s)
    with pytest.raises(FileNotFoundError):
        cache.load(s)
