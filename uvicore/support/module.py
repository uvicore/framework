import glob
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
    """Import module from string"""
    # Detect if wildcard some.module.*
    # If so, we will import EACH file in that directory
    # Meaning no __init__.py required to load all
    wildcard = False
    if module[-2:] == '.*':
        wildcard = True
        module = module[0:-2]

    # Explode parts
    parts = module.split('.')
    path = '.'.join(parts[0:-1])
    name = ''.join(parts[-1:])

    # Try to import assuming module string is an object, a file or a package (with __init__.py)
    #try:
    # Namespace means you are importing a folder without a __init__.py
    namespace = False
    root = False

    # Root means you are importing a single module without a path
    # like just 'uvicore'
    if path == '': root = True

    if namespace or root:
        imported = import_module(module)
    else:
        try:
            imported = import_module(module)
            namespace = True
        except ModuleNotFoundError:
            imported = import_module(path)

    # Example when importing an actual dictiony called app
    # from uvicore.foundation.config.app.app
    # imported.__name__ # uvicore.foundation.config.app
    # imported.__package__ # uvicore.foundation.config
    # imported.__file__ # /home/mreschke/Code...

    # Get actual imported object
    if namespace or root:
        object = imported
    else:
        #try:
        #dump('hi', imported)
        object = getattr(imported, name)
        #except:
        #    raise Exception("There was an error while dynamically importing " + module + '.  Check for errors in that file.')

    # File can be actual file.py or __init__.py or just the folder
    # if its a namespace import
    file = imported.__file__ or imported.__path__._path[0]

    if wildcard:
        pyfiles = glob.glob(file + '/*.py')
        for pyfile in pyfiles:
            # Recursively load each .py file in this folder
            modname = pyfile.split('/')[-1].split('.')[0]
            load(module + '.' + modname)
        # No need to load actual namespace module since we load .*
        return

    # Build our Module() object for return
    mod = Module(
        object=object,
        name=name,
        path=path if path else name,
        fullpath=path + '.' + name if path else name,
        package=imported.__package__,
        file=file
    )
    return mod
    # except:
    #     raise ModuleNotFoundError("Could not dynamically load module {}".format(module))

def location(module: str) -> str:
    """Find modules folder path (not file path) without importing it"""

    try:
        # Module is a package or namespace package
        spec = find_spec(module)
        return spec.submodule_search_locations[0]
    except:
        # Module is actual file or class/method inside a file
        try:
            spec = find_spec('.'.join(module.split('.')[0:-1]))
            if spec.submodule_search_locations:
                # Module is actual file
                return spec.submodule_search_locations[0]
            else:
                # Module is a class/method inside a file
                spec = find_spec('.'.join(module.split('.')[0:-2]))
                return spec.submodule_search_locations[0]
        except:
            return None



    # if spec.submodule_search_locations[0]:
    #     return spec.submodule_search_locations[0]
    # else:
    #     return spec.origin
