from typing import Generic, List, TypeVar, Union

import uvicore
from uvicore.contracts import Application, Package
from uvicore.http.routing import APIRouter, WebRouter
from uvicore.support.module import load

# Generic Router (APIRouter or WebRouter)
R = TypeVar('R')

class Routes(Generic[R]):

    app: Application
    package: Package


    def __init__(self, app: Application, package: Package, Router: R, prefix: str):
        self.package = package
        self._Router: R = Router
        self.prefix = prefix

        # Register routes
        self.register()

    def include(self, module, *, prefix: str = '', tags: List[str] = None) -> None:
        #self.http.controller(controller.route, prefix=self.prefix)
        if type(module) == str:
            # Using a string to point to an endpoint class controller
            controller = load(self.endpoints + '.' + module + '.route')
            uvicore.app.http.include_router(
                controller.mod,
                prefix=self.prefix + str(prefix),
                tags=tags,
            )
        else:
            # Passing in an actual router class
            uvicore.app.http.include_router(
                module,
                prefix=self.prefix + str(prefix),
                tags=tags,
            )

    def Router(self) -> R:
        return self._Router()
