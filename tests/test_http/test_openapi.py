import re
import pytest
import uvicore
from uvicore.support.dumper import dump


def test_swagger_ui_default_models_expansion_hides_schemas():
    """get_swagger_ui_html defaults defaultModelsExpandDepth to -1 (hide Schemas section)"""
    from uvicore.http.openapi.docs import get_swagger_ui_html
    html = get_swagger_ui_html(openapi_url='/x', title='t').body.decode()
    match = re.search(r'defaultModelsExpandDepth:\s*(-?\d+)', html)
    assert match is not None, "defaultModelsExpandDepth not rendered into Swagger UI"
    assert match.group(1) == '-1'


def test_swagger_ui_models_expansion_is_configurable():
    """models_expansion arg flows through to Swagger UI defaultModelsExpandDepth"""
    from uvicore.http.openapi.docs import get_swagger_ui_html
    html = get_swagger_ui_html(openapi_url='/x', title='t', models_expansion=1).body.decode()
    match = re.search(r'defaultModelsExpandDepth:\s*(-?\d+)', html)
    assert match is not None
    assert match.group(1) == '1'


@pytest.mark.asyncio
async def test_api_server_built_with_separate_schemas_disabled(app1):
    """
    Uvicore builds the API server passing FastAPI separate_input_output_schemas
    from config app.api.openapi.separate_schemas (default False).  This verifies
    the constructor wiring via the real create_http_servers() code path.

    NOTE: in pytest the live HTTP server tree is never built (is_http is forced
    False), and route merging is not idempotent across the session-scoped fixture,
    so we don't rebuild routes here, we just assert the server is constructed with
    the collapsed-schema setting.  A dummy truthy api_routes is enough to make
    create_http_servers() build the api FastAPI (it only checks truthiness).
    """
    from uvicore.http.package.bootstrap import Http
    handler = Http()
    (base_server, web_server, api_server) = handler.create_http_servers(
        web_routes={}, api_routes={'_probe': None},
    )
    assert api_server is not None, "Expected an API server to be built"
    assert api_server.separate_input_output_schemas is False


def test_fastapi_collapses_dual_use_model_when_disabled():
    """
    With separate_input_output_schemas=False a model used as BOTH request body
    and response_model is emitted once (Foo) rather than split into Foo-Input +
    Foo-Output.  This is the FastAPI behavior Uvicores default relies on.
    """
    from fastapi import FastAPI
    from pydantic import BaseModel

    class Probe(BaseModel):
        id: int
        name: str = 'x'  # a field default is what triggers FastAPIs Input/Output split

    app = FastAPI(separate_input_output_schemas=False)

    @app.post('/probe', response_model=Probe)
    def create(item: Probe):
        return item

    schemas = app.openapi()['components']['schemas']
    assert 'Probe' in schemas
    assert 'Probe-Input' not in schemas
    assert 'Probe-Output' not in schemas
