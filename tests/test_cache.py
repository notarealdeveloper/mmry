import os
import pytest
from mmry import Cache


def test_roots():
    cache = Cache()
    assert cache.name == 'global'

    cache = Cache('test')
    assert cache.name == 'test'


def test_rmtree():

    cache = Cache('test')
    n = 'key'
    i = 'input content'
    o = b'output content'

    cache.save_blob(i, o)
    cache.save_name(n, i)
    assert os.path.exists(cache.path)
    cache.rmtree(confirm=True)
    assert not os.path.exists(cache.path)

def test_blobs():

    cache = Cache('test')
    n = 'key'
    i = 'input content'
    o = b'output content'

    cache.save_blob(i, o)
    assert cache.load_blob(i) == o
    assert cache.have_blob(i)
    cache.delete_blob(i)
    assert not cache.have_blob(i)

def test_names():

    cache = Cache('test')
    n = 'key'
    i = 'input content'
    o = b'output content'

    cache.save_blob(i, o)
    cache.save_name(n, i)
    assert cache.load_name(n) == o
    assert cache.have_name(n)
    cache.delete_name(n)
    assert cache.have_blob(i)
    assert not cache.have_name(n)
    with pytest.raises(FileNotFoundError):
        cache.load_name(n)

