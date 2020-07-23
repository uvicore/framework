import importlib
import inspect

from typing import Any, Dict, List, Optional

from uvicore.contracts import Ioc as IocInterface
from uvicore.support.dumper import dd, dump
from uvicore.contracts import Binding
from uvicore.support import module

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

        # Add default binding specific to uvicore framework
        self.bind_map({
            'Application': {
                'object': 'uvicore.foundation.application._Application',
                'singleton': True,
                'aliases': ['App', 'app'],
            },
            'Config': {
                'object': 'uvicore.configuration.config._Config',
                'singleton': True,
                'aliases': ['Configuration', 'config'],
            },
            'Package': {
                'object': 'uvicore.foundation.package._Package',
                'aliases': ['package'],
            },
            # 'Logger': {
            #     'object': 'uvicore.support.logger._Logger',
            #     'factory': 'uvicore.factory.Logger',
            #     'singleton': True,
            #     'aliases': ['Log', 'log', 'logger'],
            # },
        })

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
            # If object is None, dynamically import object from path
            binding.object = module.load(binding.path).object

        # Determine type
        is_class = inspect.isclass(binding.object)
        is_singleton = is_class and binding.singleton
        kwargs = binding.kwargs or {}

        # Instantiate a singleton only once
        made = None
        if is_singleton:
            if not binding.instance:
                if binding.factory:
                    factory = module.load(binding.factory).object
                    binding.instance = factory().make(binding.object, **kwargs)
                else:
                    binding.instance = binding.object(**kwargs)
            made = binding.instance

        # Instantiate a non-singleton every time
        # Unless there is no factory and no kwargs, simply return the object class
        elif is_class:
            if binding.factory:
                factory = module.load(binding.factory).object
                made = factory().make(binding.object, **kwargs)
            elif binding.kwargs:
                made = binding.object(**kwargs)
            else:
                made = binding.object

        # Bind is not a class.  Must be a method or module, return it
        else:
            made = binding.object

        # Return made object
        return made

    def bind(self,
        name: str,
        object: Any,
        *,
        factory: Any = None,
        kwargs: Dict = None,
        singleton: bool = False,
        aliases: List = []
    ) -> None:
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
                factory=factory,
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
                factory=factory,
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

# Public API for import * and doc gens
__all__ = ['Ioc']
