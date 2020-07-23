from importlib import import_module
from importlib.util import find_spec
from dataclasses import dataclass
from uvicore.support.dumper import dump, dd
from typing import Any, NamedTuple

@dataclass
class Module():
    """Dynamic imported module interface"""
    object: Any
    name: str
    path: str
    fullpath: str
    package: str
    file: str

def load(module: str) -> Module:
    """Import module from string
    """
    parts = module.split('.')
    path = '.'.join(parts[0:-1])
    name = ''.join(parts[-1:])

    # Try to import assuming module string is an object, a file or a package (with __init__.py)
    try:
        if path == '':
            imported = import_module(module)
        else:
            imported = import_module(path)

        # Example when importing an actual dictiony called app
        # from uvicore.foundation.config.app.app
        # imported.__name__ # uvicore.foundation.config.app
        # imported.__package__ # uvicore.foundation.config
        # imported.__file__ # /home/mreschke/Code...

        if path == '':
            object = imported
        else:
            object = getattr(imported, name)

        return Module(
            object=object,
            name=name,
            path=path,
            fullpath=path + '.' + name,
            package=imported.__package__,
            file=imported.__file__,
        )
    except:
        raise ModuleNotFoundError("Could not dynamically load module {}".format(module))

def location(module: str) -> str:
    """Find modules folder path (not file path) without importing it
    """
    try:
        spec = find_spec(module)
    except:
        spec = find_spec('.'.join(module.split('.')[0:-1]))
    return spec.submodule_search_locations[0]
    # if spec.submodule_search_locations[0]:
    #     return spec.submodule_search_locations[0]
    # else:
    #     return spec.origin
