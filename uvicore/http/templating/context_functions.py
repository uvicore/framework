import uvicore
from typing import Any


def url(context: dict, name: str, **path_params: Any) -> str:
    request = context["request"]
    return request.url_for(name, **path_params)

def asset(context: dict, path: str) -> str:

    # Detect custom host and path
    asset_host = uvicore.config.app.web.asset.host
    asset_path = uvicore.config.app.web.asset.path or '/assets'

    if asset_host:
        # Using a custom asset host
        return asset_host + asset_path + '/' + path
    else:
        # Use the current running servers domain as the base URL
        request = context["request"]
        return request.url_for('assets', path=path)

def public(context: dict, path: str) -> str:
    request = context["request"]
    return request.url_for('public', path=path)

