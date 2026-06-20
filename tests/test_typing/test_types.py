import pytest
import uvicore
from uvicore.typing import Dict, OrderedDict, List
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_dict_class_basic(app1):
    """Test Dict class basic functionality"""
    d = Dict({'a': 1, 'b': 2})
    assert d['a'] == 1
    assert d.a == 1


@pytest.mark.asyncio
async def test_dict_set_attribute(app1):
    """Test Dict set via attribute"""
    d = Dict()
    d.name = 'test'
    assert d['name'] == 'test'
    assert d.name == 'test'


@pytest.mark.asyncio
async def test_dict_get_method(app1):
    """Test Dict get method"""
    d = Dict({'x': 10})
    assert d.get('x') == 10
    assert d.get('missing', 'default') == 'default'


@pytest.mark.asyncio
async def test_dict_keys_values(app1):
    """Test Dict keys and values"""
    d = Dict({'a': 1, 'b': 2})
    assert 'a' in d.keys()
    assert 1 in d.values()


@pytest.mark.asyncio
async def test_dict_update(app1):
    """Test Dict update"""
    d = Dict({'a': 1})
    d.update({'b': 2})
    assert d.b == 2


@pytest.mark.asyncio
async def test_dict_pop(app1):
    """Test Dict pop"""
    d = Dict({'a': 1, 'b': 2})
    value = d.pop('a')
    assert value == 1
    assert 'a' not in d


@pytest.mark.asyncio
async def test_dict_merge(app1):
    """Test Dict merge"""
    d1 = Dict({'a': 1})
    d2 = Dict({'b': 2})
    merged = d1.merge(d2)
    assert 'a' in merged
    assert 'b' in merged


@pytest.mark.asyncio
async def test_ordered_dict_class(app1):
    """Test OrderedDict class"""
    od = OrderedDict({'c': 3, 'a': 1, 'b': 2})
    assert od is not None


@pytest.mark.asyncio
async def test_list_type_hint(app1):
    """Test List type hint"""
    items: List[str] = ['a', 'b']
    assert len(items) == 2
