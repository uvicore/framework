import uvicore
from uvicore.http.request import Request


@uvicore.composer()
class Layout:
    """App1 test view composer.  Registered as app1/* in the app1 provider."""

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
        # Merged into the context of every view matching this composer's wildcard
        return {
            'composed_marker': 'app1-layout',
        }
