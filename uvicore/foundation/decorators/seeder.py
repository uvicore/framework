import uvicore
from typing import Any, Dict, List

def seeder(name: str = None):
    def decorator(cls):
        # Bind this seeder into the Ioc
        bind_name = name or cls.__module__ + '.' + cls.__name__
        new_cls = uvicore.ioc.bind_from_decorator(cls, name=bind_name, object_type='seeder', singleton=False)

        # Other things with a seeder

        return new_cls
    return decorator
