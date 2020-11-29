from .request import Request
from .routing import ApiRouter, Routes, WebRouter

# NO - not used by user
#from .server import Server
# static.StaticFiles

# Do not import response, we want to import it as a file to use as a namespace
# from uvicore.http import response
# response.View() or response.Text().... so its a namespace

# The http package uses a __init__.py because users will import these
# methods from their own controllers and we want a nicer import which looks
# like - from uvicore.http import Request
