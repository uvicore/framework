import os
import typer
import uvicorn
import uvicore
from subprocess import Popen


cli = typer.Typer()

@cli.command()
def serve():
    """Unicorn dev server (reload and logs)
    """
    # Uvicorn dev server info
    appname = uvicore.config('app.server.app')
    host = uvicore.config('app.server.host')
    port = uvicore.config('app.server.port')
    autoreload = uvicore.config('app.server.reload')
    access_log = uvicore.config('app.server.access_log')

    # Run Uvicorn server
    uvicorn.run(appname, host=host, port=port, reload=autoreload, access_log=access_log)
