# type: ignore
from typing import *
from .dictionary import Dict, OrderedDict
try:
    from starlette.types import Scope, Message, Receive, Send, ASGIApp
except:
    Scope = None
    Message = None
    Receive = None
    Send = None
    ASGIApp = None

# Decorator Type Helper
# def handle() -> Callable[[Decorator], Decorator]:
#     def decorator(func: Decorator) -> Decorator
#         return func
#     return decorator
Decorator = TypeVar("Decorator", bound=Callable[..., Any])

# from __future__ import annotations
# from typing import *
# import copy
# #from uvicore.typing.dictionary import _SuperDict
# from collections import OrderedDict as _OrderedDict
# from uvicore.support.dumper import dump, dd
# from prettyprinter import pretty_call, register_pretty







# class _DictOLD:
#     def __getattr__(self, key):
#         """Getting a value by dot notation, pull from dictionary"""
#         ret = self.get(key)

#         # If key not in self dict, throw error
#         # This also hits if you do hasattr(x, y)
#         # NO, or else I can't do mydict.services or None of key doesn't exist
#         # This means I cannot use hasattr(x, y)
#         #if key not in self:
#         #    raise AttributeError()

#         # If key does exist but is None AND starts with __
#         if not ret and key.startswith("__"):
#             raise AttributeError()

#         # Key exists, even None, return value
#         return ret

#     def __setattr__(self, key, value):
#         self[key] = value

#     def __getstate__(self):
#         return self

#     def __setstate__(self, d):
#         self.update(d)

#     def copy(self):
#         """Create a clone copy of this dict"""
#         return self.__class__(dict(self).copy())

#     def update(self, d):
#         """Extend a dictionary with another dictionary"""
#         super(self.__class__, self).update(d)
#         return self

#     def merge(self, d):
#         """Deep merge self with this new dictionary"""
#         self.update(_deep_merge(d, self))
#         return self

#     def defaults(self, d):
#         """Provide defaults, essentially a reverse merge"""
#         self.update(_deep_merge(self, d))
#         return self

#     def extend(self, d):
#         """Alias for update"""
#         return self.update(d)

#     def clone(self):
#         """Alias of copy"""
#         return self.copy()

#     def hasattr(self, key):
#         return key in self



