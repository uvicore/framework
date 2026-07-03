import uvicore
from uvicore.http.request import Request


@uvicore.composer()
class Layout:
    """Site-wide layout composer.

    Registered against the ``app1/*`` wildcard in the app1 provider, so every
    page's context (and therefore the shared ``layouts/app.j2``) receives this
    data without each controller having to pass it.  This is the idiomatic way
    to feed a header/footer/nav from one place.
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
        # Merged into the context of every view matching this composer's wildcard.
        # NOTE: 'composed_marker' is asserted by tests/test_http/test_view_composers.py
        # and must remain 'app1-layout'.
        return {
            'composed_marker': 'app1-layout',
            'site_name': 'Uvicore Web',
            'site_tagline': 'The performance of FastAPI with the elegance of Laravel',
            'year': 2026,
            # Primary navigation.  Templates render each item via url(item.route),
            # so route names live in exactly one place.
            'nav': [
                {'label': 'Home', 'route': 'home'},
                {'label': 'About', 'route': 'app1.about'},
                {'label': 'Features', 'route': 'app1.features'},
                {'label': 'Contact', 'route': 'app1.contact'},
                {'label': 'Login', 'route': 'app1.login'},
                {'label': 'Admin', 'route': 'app1.admin'},
            ],
        }
