from collections import OrderedDict

def getvalue(object, key):
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

def setvalue(object, key, value):
    """Set a dict or class instance attribute value in a unified way"""
    if type(object) == dict or type(object) == OrderedDict:
        # Dict or OrderedDict
        object[key] = value
    else:
        # Class instance
        setattr(object, key, value)


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

