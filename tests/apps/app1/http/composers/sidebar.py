import uvicore
from uvicore.http.request import Request


@uvicore.composer()
class Sidebar:
    """App1 test view composer.  Registered on specific app1 views."""

    def __init__(self,
        request: Request,
        name: str,
        context: dict,
        status_code: int,
        headers: dict,
        media_type: str,
    ) -> None:
        self.request = request
        self.name = name
        self.context = context
        self.status_code = status_code
        self.headers = headers
        self.media_type = media_type

    async def compose(self) -> dict:
        return {
            'sidebar_marker': 'app1-sidebar',
        }
