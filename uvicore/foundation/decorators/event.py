import uvicore
from uvicore.typing import Callable, Decorator


def event(name: str = None) -> Callable[[Decorator], Decorator]:
    def decorator(cls: Decorator) -> Decorator:
        # Bind this Event into the Ioc
        bind_name = name or cls.__module__ + '.' + cls.__name__
        new_cls = uvicore.ioc.bind_from_decorator(cls, name=bind_name, object_type='event', singleton=False)

        # Other things with an event

        return new_cls
    return decorator
