import uvicore
from uvicore.contracts import Application as ApplicationInterface

@uvicore.service()
class Handler:

    @property
    def app(self) -> ApplicationInterface:
        return self._app

    def __init__(self, app: ApplicationInterface):
        self._app = app
