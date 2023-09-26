from typing import Optional

import uvicore
from uvicore import app, log
from uvicore.console import command
from uvicore.support.dumper import dd, dump

@command()
def list(): # pragma: no cover
    """Show all Web and API Routes"""
    log.header("Final Merged Web and API Routes")
    log.line()
    dd({
        'web': app.running_config.http.web.routes,
        'api': app.running_config.http.api.routes,
    })

