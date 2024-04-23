import json
from uvicore.typing import Optional, Any, Dict
from starlette.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_oauth2_redirect_html
from fastapi.encoders import jsonable_encoder

def get_rapidoc_ui_html(
    *,
    openapi_url: str
) -> HTMLResponse:

    html = f"""
        <!doctype html>
        <head>
        <script type="module" src="https://unpkg.com/rapidoc/dist/rapidoc-min.js"></script>
        </head>
        <body>
        <rapi-doc spec-url="{openapi_url}" >
        </rapi-doc>
        </body>
    """
    return HTMLResponse(html)


def get_rapidoc_pdf_ui_html(
    *,
    openapi_url: str
) -> HTMLResponse:
    html = f"""
        <!doctype html>
        <html>
        <head>
        <script src="https://unpkg.com/rapipdf/dist/rapipdf-min.js"></script>
        </head>
        <body>
        <rapi-pdf
            style = "width:700px; height:40px; font-size:18px;"
            spec-url = "{openapi_url}"
            button-bg = "#b44646"
        > </rapi-pdf>
        </body>
        </html>
    """
    return HTMLResponse(html)


def get_rapidoc_ui_oauth2_redirect_html() -> HTMLResponse:
    html = f"""
        <!DOCTYPE html>
        <html lang=en>
        <head>
            <title>RapiDoc UI</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width,minimum-scale=1,initial-scale=1,user-scalable=yes">
            <script type="module" src="rapidoc-min.js"></script>
        </head>
        <body>
            <noscript><strong>We're sorry but RapiDoc doesn't work properly without JavaScript enabled. Please enable it to continue.</strong></noscript>
            <oauth-receiver> </oauth-receiver>
        </body>
        </html>
    """
    return HTMLResponse(html)
