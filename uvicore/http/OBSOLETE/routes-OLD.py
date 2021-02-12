


# @uvicore.service()
# class Routes(RoutesInterface, Generic[R]):

#     endpoints: str = None

#     @property
#     def app(self) -> ApplicationInterface:
#         return self._app

#     @property
#     def package(self) -> PackageInterface:
#         return self._package

#     @property
#     def Router(self) -> R:
#         return self._Router

#     @property
#     def prefix(self) -> str:
#         return self._prefix

#     def __init__(self,
#         app: ApplicationInterface,
#         package: PackageInterface,
#         Router: R,
#         prefix: str
#     ):
#         self._app = app
#         self._package = package
#         self._Router = Router
#         self._prefix = prefix


#     def new_router(self):
#         router = self.Router()

#         # Add route context into Router
#         router.uvicore = Dict({
#             'prefix': self.prefix,
#             'endpoints': self.endpoints,
#         })
#         return router


#     def include(self, module, *, prefix: str = '', tags: List[str] = None) -> None:
#         #self.http.controller(controller.route, prefix=self.prefix)

#         if type(module) == str:
#             # Using a string to point to an endpoint class controller
#             controller = load(self.endpoints + '.' + module + '.route')
#             uvicore.app.http.include_router(
#                 controller.object,
#                 prefix=self.prefix + str(prefix),
#                 tags=tags,
#             )
#         else:
#             # Passing in an actual router class
#             uvicore.app.http.include_router(
#                 module,
#                 prefix=self.prefix + str(prefix),
#                 tags=tags,
#             )

#     # def Router(self) -> R:
#     #     return self._Router()


# # IoC Class Instance
# #Routes: RoutesInterface = uvicore.ioc.make('Routes', _Routes)

# # Public API for import * and doc gens
# #__all__ = ['Routes', '_Routes']
