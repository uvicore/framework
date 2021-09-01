import uvicore
from uvicore.support.dumper import dd, dump
from uvicore.contracts import UserInfo
from uvicore.http import Request, response
from uvicore.http.routing import WebRouter, Controller, Guard


@uvicore.controller()
class Rapidoc(Controller):

    def register(self, route: WebRouter):

        @route.get('/rapidoc')
        async def about(request: Request):
            return response.HTML("""
        <!doctype html> <!-- Important: must specify -->
        <html>
        <head>
        <meta charset="utf-8"> <!-- Important: rapi-doc uses utf8 charecters -->
        <script type="module" src="https://unpkg.com/rapidoc/dist/rapidoc-min.js"></script>
        </head>
        <body>
        <rapi-doc spec-url = "http://localhost:5000/api/openapi.json"> </rapi-doc>
        </body>
        </html>
        """)

        # Return router
        return route
