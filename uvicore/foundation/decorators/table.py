import uvicore
from uvicore.typing import Callable, Decorator


def table(name: str = None) -> Callable[[Decorator], Decorator]:
    def decorator(cls: Decorator) -> Decorator:
        # Bind this table into the Ioc
        bind_name = name or cls.__module__ + '.' + cls.__name__
        new_cls = uvicore.ioc.bind_from_decorator(cls, name=bind_name, object_type='table', singleton=True)

        # Other things with a table

        return new_cls
    return decorator
