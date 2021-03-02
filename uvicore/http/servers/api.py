import uvicore
from fastapi import FastAPI as _FastAPI
from uvicore.support.dumper import dd, dump


@uvicore.service('uvicore.http.servers.api._Server',
    #aliases=['api', 'web_server'],
    singleton=True,
    kwargs={
        'debug': uvicore.config('app.debug'),
        'title': uvicore.config('app.api.openapi.title'),
        'version': uvicore.app.version,
        'openapi_url': uvicore.config('app.api.openapi.url'),
        'docs_url': uvicore.config('app.api.openapi.docs_url'),
        'redoc_url': uvicore.config('app.api.openapi.redoc_url'),
        #'root_path': uvicore.config('app.api.root_path'), # experiment with using Kong for API but Nginx for Web, may need 2 root_paths
    },
)
class Server(_FastAPI):
    @property
    def server(self) -> _FastAPI:
        return self
