import uvicore
from uvicore.typing import Callable, Decorator


def controller(name: str = None) -> Callable[[Decorator], Decorator]:
    def decorator(cls: Decorator) -> Decorator:
        # Bind Routes into the Ioc
        bind_name = name or cls.__module__ + '.' + cls.__name__
        new_cls = uvicore.ioc.bind_from_decorator(cls, name=bind_name, object_type='controller', singleton=False)
        return new_cls
    return decorator
