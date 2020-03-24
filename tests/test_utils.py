import pytest

from mppm.utils import lazy_property

class LazyPropertyClass:
    def __init__(self):
        self._counter = 0

    @lazy_property
    def counter(self):
        self._counter += 1
        return self._counter

@pytest.fixture()
def lazyproperty():
    yield LazyPropertyClass()

class TestLazyProperty:
    def test_get(self, lazyproperty):
        assert lazyproperty.counter == 1

    def test_getattr(self, lazyproperty):
        assert getattr(lazyproperty, "counter") == 1

    def test_lazy(self, lazyproperty):
        assert lazyproperty.counter == 1
        assert lazyproperty.counter == 1

    def test_del_doesnt_exist(self, lazyproperty):
        with pytest.raises(AttributeError) as e:
            del lazyproperty.counter
        assert lazyproperty.counter == 1

    def test_del(self, lazyproperty):
        assert lazyproperty.counter == 1
        del lazyproperty.counter
        assert lazyproperty.counter == 2

    def test_delattr(self, lazyproperty):
        assert lazyproperty.counter == 1
        delattr(lazyproperty, "counter")
        assert lazyproperty.counter == 2

    def test_set(self, lazyproperty):
        lazyproperty.counter = 10
        assert lazyproperty.counter == 10

    def test_setattr(self, lazyproperty):
        setattr(lazyproperty, "counter", 10)
        assert lazyproperty.counter == 10

    def test_overwrite(self, lazyproperty):
        lazyproperty.counter = 10
        assert lazyproperty.counter == 10
        lazyproperty.counter = 20
        assert lazyproperty.counter == 20

    def test_get_from_class(self):
        assert isinstance(LazyPropertyClass.counter, lazy_property)