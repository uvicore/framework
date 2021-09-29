import uvicore
from uvicore.http.request import Request


@uvicore.composer()
class xx_ComposerName:
    """xx_ComposerName view composer"""

    def __init__(self,
        request: Request,
        name: str,
        context: dict,
        status_code: int,
        headers: dict,
        media_type: str
    ) -> None:
        self.request = request
        self.name = name
        self.context = context
        self.status_code = status_code
        self.headers = headers
        self.media_type = media_type

    async def compose(self) -> dict:
        # This composer is registered in your service provider boot() method.
        # Example: self.composer('xx_vendor.xx_appname.http.composers.xx_composername.xx_ComposerName', ['xx_appname/*'])

        # Return new context to merge into views
        return {
            'example': 'available to your views that match the composer wildcard',
        }
