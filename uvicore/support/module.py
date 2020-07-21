from importlib import import_module
from importlib.util import find_spec
from typing import NamedTuple
from uvicore.support.dumper import dump, dd


class Module(NamedTuple):
    """Dynamic imported module interface
    """
    mod: any
    name: str
    path: str
    fullpath: str
    origin: str

def load(module: str) -> Module:
    """Import module from string
    """
    parts = module.split('.')
    path = '.'.join(parts[0:-1])
    name = ''.join(parts[-1:])
    try:
        # Try to import assuming module string is an actual file or package with __init__.py
        imported = import_module(path)
        return Module(
            mod=getattr(imported, name),
            name=name,
            path=path,
            fullpath=path + '.' + name,
            origin=imported.__file__,
        )
    except:
        try:
            # If not a file or package, assume module string is a namespace package
            imported = import_module(path)
            return Module(
                mod=imported,
                name=name,
                path=path,
                fullpath=path + '.' + name,
                origin=imported.__file__,
            )
        except:
            raise ModuleNotFoundError

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
