# type: ignore
from .request import Request
from starlette.background import BackgroundTask, BackgroundTasks

# No, causes to much to be imported just by importing anything from uvicore.http
# from .routing import (ApiRoute, ApiRouter, Controller, ModelRouter, Router,
#                       Routes, WebRoute, WebRouter)


# NO - not used by user
#from .server import Server
# static.StaticFiles

# Do not import response, we want to import it as a file to use as a namespace
# from uvicore.http import response
# response.View() or response.Text().... so its a namespace

# The http package uses a __init__.py because users will import these
# methods from their own controllers and we want a nicer import which looks
# like - from uvicore.http import Request
