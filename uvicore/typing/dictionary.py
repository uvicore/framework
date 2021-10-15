import re
import copy
from uvicore.support.dumper import dump, dd
from collections import OrderedDict as _OrderedDict
from prettyprinter import pretty_call, register_pretty


# Builtin Dict Methods
# clear
# copy
# popitem
# setdefault
# update
# fromkeys


class _SuperDict:
    """Advanced python dictionary and ordered dictionary replacement"""
    # A refactor of https://github.com/mewwts/addict (MIT)

    def __init__(__self, *args, **kwargs):
        object.__setattr__(__self, '__parent', kwargs.pop('__parent', None))
        object.__setattr__(__self, '__key', kwargs.pop('__key', None))
        object.__setattr__(__self, '__frozen', False)
        for arg in args:
            if not arg: continue

            if isinstance(arg, dict):
                for key, val in arg.items():
                    __self[key] = __self._hook(val)
            elif isinstance(arg, tuple) and (not isinstance(arg[0], tuple)):
                __self[arg[0]] = __self._hook(arg[1])
            else:
                for key, val in iter(arg):
                    __self[key] = __self._hook(val)

        for key, val in kwargs.items():
            __self[key] = __self._hook(val)


    def __call__(self, dotkey: str = None):
        return self.dotget(dotkey)

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __setattr__(self, name, value):
        """Set new attribute and detect if it is a reserved keyword if the dict class"""
        if hasattr(self.__class__, name):
            msg = "'Dict' object attribute '{}' is read-only"
            raise AttributeError(msg.format(name))
        self[name] = value

    def __delattr__(self, name):
        del self[name]

    def __setitem__(self, name, value):
        # Check if dict is frozen (read only)
        frozen = (hasattr(self, '__frozen') and object.__getattribute__(self, '__frozen'))
        if frozen and name not in super(_SuperDict, self).keys():
            msg = 'Dictionary is frozen / readonly.'
            raise KeyError(msg)

        super(_SuperDict, self).__setitem__(name, value)
        try:
            p = object.__getattribute__(self, '__parent')
            key = object.__getattribute__(self, '__key')
        except AttributeError:
            p = None
            key = None
        if p is not None:
            p[key] = self
            object.__delattr__(self, '__parent')
            object.__delattr__(self, '__key')

    def __add__(self, other):
        if not self.keys(): return other

        self_type = type(self).__name__
        other_type = type(other).__name__
        msg = "Unsupported operand type(s) for +: '{}' and '{}'"
        raise TypeError(msg.format(self_type, other_type))

    def __missing__(self, name):
        # If missing, create a new Dict, unless frozen
        #frozen = (hasattr(self, '__frozen') and object.__getattribute__(self, '__frozen'))
        frozen = object.__getattribute__(self, '__frozen')
        if frozen:
           raise KeyError(name)
        # Don't use self to make a new blank key as it could be OrderedDict
        # We always want a missing value to be an actual SuperDict
        #return self.__class__(__parent=self, __key=name)
        return Dict(__parent=self, __key=name)

    def __getnewargs__(self):
        return tuple(self.items())

    def __getstate__(self):
        return self

    def __setstate__(self, state):
        self.update(state)

    def __or__(self, other):
        if not isinstance(other, (_SuperDict, dict)):
            return NotImplemented
        new = self.__class__(self)
        new.update(other)
        return new

    def __ror__(self, other):
        if not isinstance(other, (_SuperDict, dict)):
            return NotImplemented
        new = self.__class__(other)
        new.update(self)
        return new

    def __ior__(self, other):
        self.update(other)
        return self

    def __deepcopy__(self, memo):
        other = self.__class__()
        memo[id(self)] = other
        for key, value in self.items():
            other[copy.deepcopy(key, memo)] = copy.deepcopy(value, memo)
        return other

    @classmethod
    def _hook(cls, item):
        if isinstance(item, _SuperDict):
            # Already a SuperDict (Dict or OrderedDict) don't reconvert
            return item
        elif isinstance(item, dict):
            # A standard builtin dict, convert to SuperDict
            # Do NOT however use cls(item) as that will convert to the same type
            # this one is.  In the case of OrderedDict all sub dicts will become
            # OrderedDicts, which we don't want.  Only explicity defined OrderedDicts
            # should be kept intact.  Any sub dict under that should be an our Dict
            #return cls(item)
            return Dict(item)
        elif isinstance(item, (list, tuple)):
            # A List or tuple
            return type(item)(cls._hook(elem) for elem in item)
        return item

    def copy(self):
        """Make a byvalue copy of entire dict

        This overrides the builtin dict method."""
        return copy.copy(self)

    def deepcopy(self):
        """Make a byvalue copy of entire dict"""
        return copy.deepcopy(self)

    def clone(self):
        """Alias of deepcopy"""
        return self.deepcopy()

    def update(self, *args, **kwargs):
        """Deep merge one or more dictionaries with self.  Overwrites values that exist.

        This overrides the builtin dict method."""
        other = {}
        if args:
            if len(args) > 1: raise TypeError()
            # Add in arguments (assumed a dict), convert to SuperDict
            other.update(self.__class__(args[0]))
        other.update(kwargs)
        for k, v in other.items():
            if ((k not in self) or (not isinstance(self[k], dict)) or (not isinstance(v, dict))):
                # Add in any NON dictionary items that do not exist
                self[k] = v
            else:
                # Add in dictionary items, convert to SuperDict
                self[k].update(self.__class__(v))
        return self

    def merge(self, *args, **kwargs):
        """Deep merge one or more dictionaries with self.  Overwrites values that exist."""
        self.update(*args, **kwargs)
        return self

    def defaults(self, *args, **kwargs):
        """Provide defaults Dict to existing self and add only if not exists.
        Essentially a reverse merge that does NOT overwrite values if exist"""
        defaults = self.__class__(*args, **kwargs)
        defaults.merge(self)
        self.merge(defaults)
        return self

    def setdefault(self, key: str, default=None):
        """Set a single key value only if not exists.

        This overrides the builtin dict method."""
        # if key in self:
        #     return self[key]
        # else:
        #     self[key] = default
        #     return default

        if key not in self:
            self[key] = default
        return self

    def to_dict(self):
        """Convert SuperDict into regular builtin dict"""
        base = {}
        for key, value in self.items():
            if isinstance(value, type(self)):
                base[key] = value.to_dict()
            elif isinstance(value, (list, tuple)):
                base[key] = type(value)(
                    item.to_dict() if isinstance(item, type(self)) else
                    item for item in value)
            else:
                base[key] = value
        return base

    def dict(self):
        """Convert SuperDict into regular builtin dict"""
        # Why to_dict() and dict().  Pydantic has a dict(), so I want to mimic
        # so all calls to dict() on SuperDict or Pydanttic models work the same
        # Mostly for uvicore orm usage.
        return self.to_dict()

    def freeze(self, freeze=True):
        """Set entire SuperDict to read only"""
        object.__setattr__(self, '__frozen', freeze)
        for key, val in self.items():
            if isinstance(val, _SuperDict):
                val.freeze(freeze)

    def unfreeze(self):
        """Set entire SuperDict to writeable"""
        self.freeze(freeze=False)

    def dotget(self, dotkey: str = None, _recursive_config = None):
        """Get values using string dot notation.  Surround with [] to include those . as the key"""
        # Recursive for dot notation
        if not dotkey: return self
        if _recursive_config is None: _recursive_config = self

        try:

            # Replace any , with ^ inside [] temporarily
            if "[" in dotkey:
                def x(m): return m[0].replace('.', '^')[1:-1]
                dotkey = re.sub('(\[.*?\])', x, dotkey)

            if "." in dotkey:
                key, rest = dotkey.split(".", 1)
                key = key.replace('^', '.')
                if key not in _recursive_config:
                    _recursive_config[key] = self.__class__()
                return self.dotget(rest, _recursive_config[key])
            else:
                dotkey = dotkey.replace('^', '.')
                if dotkey in _recursive_config:
                    return _recursive_config[dotkey]
                else:
                    return self.__missing__(dotkey)
        except:
            return self.__missing__(dotkey)

    def dotset(self, dotkey: str, value, _recursive_config=None):
        """Set values using string dot notation.  Surround with [] to include those . as the key."""
        # Recursive for dot notation
        # Remember objects are byRef, so changing config also changes self.items
        if _recursive_config is None: _recursive_config = self

        # Replace any , with ^ inside [] temporarily
        if "[" in dotkey:
            def x(m): return m[0].replace('.', '^')[1:-1]
            dotkey = re.sub('(\[.*?\])', x, dotkey)

        if "." in dotkey:
            key, rest = dotkey.split(".", 1)
            key = key.replace('^', '.')
            if key not in _recursive_config:
                _recursive_config[key] = self.__class__()
            return self.dotset(rest, value, _recursive_config[key])
        else:
            # Replace ^ back with . for keys inside []
            dotkey = dotkey.replace('^', '.')
            if type(value) == dict:
                _recursive_config[dotkey] = self.__class__(value)
            else:
                _recursive_config[dotkey] = value
            return value


class Dict(_SuperDict, dict):
    """Dictionary that you can access like a class using dot notation attributes"""
    # def __init__(__self, *args, **kwargs):
    #     @register_pretty(__self.__class__)
    #     def pretty_entity(value, ctx):
    #         """Custom pretty printer for my SuperDict"""
    #         # This printer removes the class name uvicore.types.Dict and makes it print
    #         # with a regular {.  This really cleans up the output!

    #         #return pretty_call(ctx, cls, **value.__dict__)
    #         return pretty_call(ctx, '', value.to_dict())

    #     super().__init__(*args, **kwargs)
    pass



class OrderedDict(_SuperDict, _OrderedDict):
    """Ordered Dictionary that you can access like a class using dot notation attributes"""

    # def __init__(__self, *args, **kwargs):

    #     @register_pretty(__self.__class__)
    #     def pretty_entity(value, ctx):
    #         """Custom pretty printer for my SuperDict"""
    #         # This printer removes the class name uvicore.types.Dict and makes it print
    #         # with a regular {.  This really cleans up the output!

    #         #return pretty_call(ctx, cls, **value.__dict__)
    #         return pretty_call(ctx, __self.__class__, value.to_dict())

    #     super().__init__(*args, **kwargs)
    pass


@register_pretty(Dict)
def pretty_entity(value, ctx):
    """Custom pretty printer for my SuperDict"""
    # This printer removes the class name uvicore.types.Dict and makes it print
    # with a regular {.  This really cleans up the output!

    #return pretty_call(ctx, 'Dict', **value)
    #return pretty_call(ctx, 'Dict', value.to_dict())  # Does show nested dicts as SuperDicts
    return pretty_call(ctx, 'Dict', dict(**value))



@register_pretty(OrderedDict)
def pretty_entity(value, ctx):
    """Custom pretty printer for my SuperDict"""
    # This printer removes the class name uvicore.types.Dict and makes it print
    # with a regular {.  This really cleans up the output!

    #return pretty_call(ctx, 'OrderedDict', **value)
    #return pretty_call(ctx, 'OrderedDict', value.to_dict())  # Does show nested dicts as SuperDicts
    return pretty_call(ctx, 'OrderedDict', dict(**value))


