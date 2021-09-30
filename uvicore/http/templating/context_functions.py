import uvicore
from typing import Any
from uvicore.support.dumper import dump, dd


def url(context: dict, name: str, **path_params: Any) -> str:
    # Get http configuration
    config = uvicore.config.app.http

    # Get request from context
    request = context["request"]

    # Get full URL from starlette's request url_for() method
    try:
        url = request.url_for(name, **path_params)
    except Exception as e:
        raise Exception('Could not find URL for {} in template {}'.format(name, context.name))

    # Ensure url contains proper x-forwarded-proto protocol
    # If serving with uvicorn this is detected properly, but if serving with
    # gunicorn it is not.  So we'll double check and force HTTPS if needed.
    if 'x-forwarded-proto' in request.headers:
        proto = request.headers['x-forwarded-proto'].lower()
        if proto == 'https' and proto not in url:
            # Starlette generated URL does not contain https, but it should
            url = 'https' + url[4:]

    # Return full URL
    return url

def asset(context: dict, path: str) -> str:

    # Detect custom host and path
    asset_host = uvicore.config.app.web.asset.host
    asset_path = uvicore.config.app.web.asset.path or '/assets'
    asset_force_https = uvicore.config.app.web.asset.force_https or False

    if asset_host:
        # Using a custom asset host
        return asset_host + asset_path + '/' + path
    else:
        # Using domain of running app
        return url(context, 'assets', path=path)

def public(context: dict, path: str) -> str:
    return url(context, 'public', path=path)

