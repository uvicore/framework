import json
from typing import Any
from uvicore.typing import Dict
from starlette.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_oauth2_redirect_html
from fastapi.encoders import jsonable_encoder

# Override fastapis get_swagger_ui_html to impliment OpenAPI docs docExpansion feature.

def get_swagger_ui_html(
    *,
    openapi_url: str,
    title: str,
    swagger_js_url: str = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.7.2/swagger-ui-bundle.js",
    swagger_css_url: str = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.7.2/swagger-ui.min.css",
    swagger_favicon_url: str = "https://fastapi.tiangolo.com/img/favicon.png",
    oauth2_redirect_url: str | None = None,
    init_oauth: Dict[str, Any] | None = None,
    doc_expansion: str = "list", # list none full
    models_expansion: int = -1, # defaultModelsExpandDepth: the bottom "Schemas" section. -1 hides it entirely, 0 collapses, 1+ expands
    model_expansion: int = 1, # defaultModelExpandDepth: the per-operation request/response model tree. 0 collapses (faster expand on large models), 1+ expands
    parameters: Dict[str, Any] | None = None, # Arbitrary extra SwaggerUIBundle parameters, merged last (override the defaults above)
) -> HTMLResponse:

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="{swagger_css_url}">
    <link rel="shortcut icon" href="{swagger_favicon_url}">
    <title>{title}</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="{swagger_js_url}"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({{
        url: '{openapi_url}',
    """

    if oauth2_redirect_url:
        html += f"oauth2RedirectUrl: window.location.origin + '{oauth2_redirect_url}',"

    html += f"""
        dom_id: '#swagger-ui',
        presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
        layout: "BaseLayout",
        deepLinking: true,
        showExtensions: true,
        showCommonExtensions: true,
        docExpansion: '{doc_expansion}',
        defaultModelsExpandDepth: {models_expansion},
        defaultModelExpandDepth: {model_expansion}"""

    # Merge any additional raw SwaggerUIBundle parameters last so they can
    # override the defaults above (e.g. defaultModelRendering, tryItOutEnabled).
    if parameters:
        for key, value in parameters.items():
            html += f",\n        {key}: {json.dumps(jsonable_encoder(value))}"

    html += """
    })"""

    if init_oauth:
        html += f"""
        ui.initOAuth({json.dumps(jsonable_encoder(init_oauth))})
        """

    html += """
    </script>
    </body>
    </html>
    """
    return HTMLResponse(html)
