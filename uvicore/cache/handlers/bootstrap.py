import uvicore
from uvicore.events import Handler
from uvicore.support.dumper import dump, dd
from uvicore.foundation.events import app as AppEvents
from uvicore.contracts import Package as Package
from uvicore.console import command_is
from starlette.applications import Starlette as _Starlette
from fastapi import FastAPI as _FastAPI
from uvicore.http import response
from uvicore.http.events import server as HttpServerEvents


class Cache(Handler):

    def __call__(self, event: AppEvents.Registered):
        """Bootstrap the Cache system after the Application is Registered"""



        dump('cache bootstrap')
