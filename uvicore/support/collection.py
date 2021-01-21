from typing import Any, Dict
from collections import OrderedDict
from collections import OrderedDict
from uvicore.support.dictionary import deep_merge
from uvicore.support.dumper import dump, dd


def getvalue(object: Any, key: Any):
    """Access a dict or class instance attribute value in a unified way"""
    if type(object) == dict or type(object) == OrderedDict:
        # Dict or OrderedDict
        return object.get(key)
    else:
        # Class instance
        if hasattr(object, key):
            return getattr(object, key)
        else:
            return None


def setvalue(object: Any, key: Any, value: Any):
    """Set a dict or class instance attribute value in a unified way"""
    if type(object) == dict or type(object) == OrderedDict:
        # Dict or OrderedDict
        object[key] = value
    else:
        # Class instance

        setattr(object, key, value)


def dotget(object: Dict, dotpath: str, default = None):
    """Access a dict or class instance attribute value by dot notation which handles nested null values well"""

    # Eliminates the need to do this if you think a child attribute may not exist
    # BAD  connection_default=custom_config.get('database').get('default') if 'database' in custom_config else None,
    # GOOD connection_default=dotget(custom_config, 'database.default')

    if '.' in dotpath:
        paths = dotpath.split('.')
    else:
        paths = [dotpath]

    node = object
    for path in paths:
        node = getvalue(node, path)
        if node is None: return default
    return node


class _Dict:
    def __getattr__(self, key):
        """Getting a value by dot notation, pull from dictionary"""
        ret = self.get(key)

        # If key not in self dict, throw error
        # This also hits if you do hasattr(x, y)
        # NO, or else I can't do mydict.services or None of key doesn't exist
        # This means I cannot use hasattr(x, y)
        #if key not in self:
        #    raise AttributeError()

        # If key does exist but is None AND starts with __
        if not ret and key.startswith("__"):
            raise AttributeError()

        # Key exists, even None, return value
        return ret

    def __setattr__(self, key, value):
        self[key] = value

    def __getstate__(self):
        return self

    def __setstate__(self, d):
        self.update(d)

    def copy(self):
        """Create a clone copy of this dict"""
        return self.__class__(dict(self).copy())

    def update(self, d):
        """Extend a dictionary with another dictionary"""
        super(self.__class__, self).update(d)
        return self

    def merge(self, d):
        """Deep merge self with this new dictionary"""
        self.update(deep_merge(d, self))
        return self

    def defaults(self, d):
        """Provide defaults, essentially a reverse merge"""
        self.update(deep_merge(self, d))
        return self

    def extend(self, d):
        """Alias for update"""
        return self.update(d)

    def clone(self):
        """Alias of copy"""
        return self.copy()

    def hasattr(self, key):
        return key in self


class Dic(dict, _Dict):
    """Dictionary that you can access like a class using dot notation attributes"""
    pass


class Odic(OrderedDict, _Dict):
    """Ordered Dictionary that you can access like a class using dot notation attributes"""
    pass




### Below is junk, experimental


class Str:
    def __init__(self, data):
        self.__data = data

    def contains(self, value):
        return value in self.__data

    def append(self, value):
        return str(self.__data) + str(value)

    def upper(self):
        return str(self.__data).upper()

    def lower(self):
        return str(self.__data).lower()


class Obj:
    def __init__(self, data):
        self.__dict__ = data

    def dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('__')}

    def __repr__(self):
        return str({k: v for k, v in self.__dict__.items() if not k.startswith('__')})


class Collection():
    # _names are protected
    # __names are private
    # @property for getters
    # @varname.setter for setters

    def __init__(self, data):
        #self.test = 'asdf'
        self.__i = 0
        self.__data = []
        #self.Object = lambda **kwargs: type("Object", (), kwargs)
        for item in data:
            #self.__data.append(self.__object(item))
            self.__data.append(Obj(item))

    def dict(self):
        items = []
        for data in self.__data:
            items.append(data.dict())
        return items

    def filter(self, callback):
        return filter(callback, self.__data)

    # def __object(self, dict):
    #     return type("Object", (), dict)

    def add(self, item):
        #self.__data.append(self.__object(item))
        self.__data.append(Obj(item))

    def __iter__(self):
        return iter(self.__data)

    def __getitem__(self, item):
        return self.__data[item]

    # @property
    # def test(self):
    #     return self.__test

    # @test.setter
    # def test(self, value):
    #     self.__test = value

    # def __next__(self):
    #     #return self.next()
    #     print('1')
    #     if len(self.data) <= self.i:
    #         self.i += 1
    #         #return self.data[self.i]
    #         return self.i
    #     else:
    #         raise StopIteration()

