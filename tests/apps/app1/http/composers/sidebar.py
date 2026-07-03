import uvicore
from uvicore.http.request import Request


@uvicore.composer()
class Sidebar:
    """Sidebar composer.

    Registered against only ``['app1/home', 'app1/about']`` in the app1 provider,
    so the sidebar appears solely on those two pages - a demonstration of
    view-specific (rather than wildcard) composer targeting.
    """

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
        # NOTE: 'sidebar_marker' is kept for parity with the layout marker and any
        # future composer assertions.
        return {
            'sidebar_marker': 'app1-sidebar',
            'sidebar_links': [
                {'label': 'Documentation', 'url': 'https://uvicore.io'},
                {'label': 'Source', 'url': 'https://github.com/uvicore/framework'},
                {'label': 'Features tour', 'route': 'app1.features'},
                {'label': 'Get in touch', 'route': 'app1.contact'},
            ],
        }
