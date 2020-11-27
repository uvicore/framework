import uvicore
from typing import Any, Dict, List

def model(name: str = None):
    def decorator(cls):
        # Bind this Model into the Ioc
        bind_name = name or cls.__module__ + '.' + cls.__name__
        new_cls = uvicore.ioc.bind_from_decorator(cls, name=bind_name, object_type='model', singleton=False)

        # Other things with a model, like add to array of models for auto-api perhaps?

        return new_cls
    return decorator
