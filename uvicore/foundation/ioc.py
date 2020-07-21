import importlib
import inspect

from typing import Any, Dict, List, Optional

from uvicore.contracts import Ioc as IocInterface
from uvicore.support.dumper import dd, dump
from uvicore.contracts import Binding


class Ioc(IocInterface):
    @property
    def bindings(self) -> Dict[str, Binding]:
        return self._bindings

    @property
    def aliases(self) -> Dict[str, str]:
        return self._aliases

    def __init__(self) -> None:
        self._bindings: Dict[str, Binding] = {}
        self._aliases: Dict[str, str] = {}

    def binding(self, name: str) -> Binding:
        if name in self.bindings:
            return self.bindings[name]
        elif name in self.aliases:
            return self.bindings[self.aliases[name]]

    def make(self, name: str) -> Any:
        """Make a module/class/method by name from IoC mapping
        """
        binding = self.binding(name)
        if not binding:
            raise ModuleNotFoundError("Could not find IoC name '{}' in mapping.".format(name))

        # If object is not defined, dynamically import it on first make (deferred)
        if not binding.object:
            # If object is None, make object from path
            # Dont use uvicore.support.module improter here as it runs down the path until it finds in importable item, we don't want that
            module_path = binding.path
            mparts = module_path.split('.')
            mpath = '.'.join(mparts[0:-1])
            mname = ''.join(mparts[-1:])
            imported = importlib.import_module(mpath)
            try:
                # Set binding.object to new import.  This does flow back to self.bindings due to ByRef nature of objects
                binding.object = getattr(imported, mname)
            except Exception as ex:
                raise ModuleNotFoundError("Could not import module {} from uvicore IoC mapping. Check your config/app.py 'ioc' mapping section.".format(module_path))

        # Instantiate singleton and store instance
        if binding.object and binding.singleton and inspect.isclass(binding.object) and not binding.instance:
            # Object is a class that should be a singleton that is not instantiated yet
            # Instantiate class and save single instantiation to container
            binding.instance = binding.object(**binding.kwargs)

        # Return singleton instance
        if binding.singleton:
            return binding.instance

        # Return object
        return binding.object

    def bind(self, name: str, object: Any, *, kwargs: Dict = {}, singleton: bool = False, aliases: List = []) -> None:
        """Add binding from method parameters
        """
        # Add each aliases to list of all aliases
        for alias in aliases:
            self._aliases[alias] = name

        # Object is a not yet imported string
        # Add to bindings without actually importing it for deferred loading
        if type(object) == str:
            binding = Binding(
                path=object,
                object=None,
                instance=None,
                kwargs=kwargs,
                singleton=singleton,
                aliases=aliases,
            )
        else:
            # Object is an actual module, class, method...
            binding = Binding(
                path=None,
                object=object,
                instance=None,
                kwargs=kwargs,
                singleton=singleton,
                aliases=aliases,
            )
        # Add binding
        self._bindings[name] = binding

    def bind_map(self, mapping: Dict) -> None:
        """Add bindings from mapping dictionary
        """
        for name, options in mapping.items():
            self.bind(name, **options)

    def alias(self, src: str, dest: str):
        """Add alias to existing binding"""
        if dest in self.bindings:
            if src not in self.bindings[dest]:
                self.bindings[dest].aliases.append(src)
