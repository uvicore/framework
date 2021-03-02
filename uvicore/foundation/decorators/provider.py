import uvicore
from uvicore.typing import Callable, Decorator

def provider(name: str = None) -> Callable[[Decorator], Decorator]:
    def decorator(cls: Decorator) -> Decorator:
        # Bind this provider into the Ioc
        bind_name = name or cls.__module__ + '.' + cls.__name__
        new_cls = uvicore.ioc.bind_from_decorator(cls, name=bind_name, object_type='provider', singleton=False)

        # Other things with a provider

        return new_cls
    return decorator
