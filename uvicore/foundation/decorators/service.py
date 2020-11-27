import uvicore
from typing import Any, Dict, List

def service(name: str = None, *, factory: Any = None, kwargs: Dict = None, singleton: bool = False, aliases: List = []) -> None:
    def decorator(cls):
        # Bind this service into the Ioc
        bind_name = name or cls.__module__ + '.' + cls.__name__
        new_cls = uvicore.ioc.bind_from_decorator(cls, name=bind_name, object_type='service', factory=factory, kwargs=kwargs, singleton=singleton, aliases=aliases)

        # Other things with a table

        return new_cls
    return decorator
