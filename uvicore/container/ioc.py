import importlib
import inspect
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

import uvicore
from uvicore.contracts import Binding
from uvicore.contracts import Ioc as IocInterface
from uvicore.support import module
from uvicore.support.dumper import dd, dump

T = TypeVar('T')

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
        # Only some early defaults are here.  The rest are bound in
        # their service providers register() method
        self.bind_map({
            'Application': {
                'object': 'uvicore.foundation.application._Application',
                'singleton': True,
                'aliases': ['App', 'app', 'application'],
            },
            'ServiceProvider': {
                'object': 'uvicore.package.provider._ServiceProvider',
                'aliases': ['service', 'provider'],
            },
            'Package': {
                'object': 'uvicore.package.package._Package',
                'aliases': ['package'],
            },
            'Dispatcher': {
                'object': 'uvicore.events.dispatcher._Dispatcher',
                'singleton': True,
                'aliases': ['dispatcher', 'Event', 'event', 'Events', 'events'],
            },
        })

    def binding(self, name: str) -> Binding:
        if name in self.bindings:
            return self.bindings[name]
        elif name in self.aliases:
            return self.bindings[self.aliases[name]]

    def make(self, name: str, default: Callable[[], T] = None, **kwargs) -> T:
        if default is not None and self.binding(name) is None:
            # Default was provided and no binding currently exists
            # Bind the default provided but look for bindings override in app_config
            object = default
            app_config = uvicore.config('app')

            if app_config.get('bindings'):
                object = app_config.get('bindings').get(name) or default
            self.bind(name, object, **kwargs)

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
                if type(binding.factory) == str:
                    # String factory, dynamically import it
                    factory = module.load(binding.factory).object
                else:
                    # Direct class factory
                    factory = binding.factory
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

    def bind(self, name: str, object: Any, *, factory: Any = None, kwargs: Dict = None, singleton: bool = False, aliases: List = []) -> None:
        # Add each aliases to list of all aliases
        for alias in aliases:
            self._aliases[alias] = name

        # Set path and object based on str or actual class
        path = None
        if type(object) == str:
            path = object
            object = None

        # Add binding
        self._bindings[name] = Binding(
            path=path,
            object=object,
            factory=factory,
            instance=None,
            kwargs=kwargs,
            singleton=singleton,
            aliases=aliases,
        )

    def bind_map(self, mapping: Dict[str, Dict]) -> None:
        for name, options in mapping.items():
            self.bind(name, **options)

    def alias(self, src: str, dest: str) -> None:
        if dest not in self.bindings:
            raise Exception('Could not find IoC binding '.format(dest))
        if src not in self.bindings[dest]:
            self.bindings[dest].aliases.append(src)
