import uvicore
from starlette.applications import Starlette as _Starlette
from uvicore.support.dumper import dd, dump


@uvicore.service('uvicore.http.servers.web._Server',
    #aliases=['api', 'web_server'],
    singleton=True,
    kwargs={
        'debug': uvicore.config('app.debug'),
    },
)
class Server(_Starlette):
    @property
    def server(self) -> _Starlette:
        return self
