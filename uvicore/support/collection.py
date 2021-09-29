from uvicore.typing import Any, Dict, Tuple, List
from collections import OrderedDict
from collections import OrderedDict
from uvicore.support.dictionary import deep_merge
from uvicore.support.dumper import dump, dd


def haskey(object: Any, key: Any) -> bool:
    """Check if value exists on a dict or class instance attribute value in a unified way"""
    if type(object) == dict or type(object) == OrderedDict:
        # Dict or OrderedDict
        return key in object
    else:
        # Class instance
        return hasattr(object, key)


def getvalue(object: Any, key: Any) -> Any:
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


def getitems(object: Any) -> List[Tuple]:
    """Get all key/value from a dict or class instance for consistent .items() iteration"""
    # With a dict you can itterate key/value with for (key,value) in dict.items()
    # but with a class you cannot.  This standardizes the items() for Dict or class.
    if type(object) == dict:
        # Dict or OrderedDict
        return object.items()
    else:
        # Class instance
        fields = []
        if getattr(object, '__fields__'):
            # Pydantic model
            fields = object.__fields__
        else:
            # Python class
            # vars(object) is the same as object.__dict__
            fields = [x for x in vars(object) if not x.startswith('__') and not callable(getattr(object, x))]
        # Return as List[Tuple] [(key, value)]
        return [(field, getattr(object, field)) for field in fields]


def setvalue(object: Any, key: Any, value: Any) -> None:
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


def unique(object: List):
    """Remove duplicates from a list while preserving the order"""
    # list(set(object)) does the unique job, but it sets to random order
    u = []
    for item in object:
        if item not in u:
            u.append(item)
    return u




### Below is junk, experimental
# These once actually used, would go into uvicore.types instead

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

