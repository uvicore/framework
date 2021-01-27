from typing import Any


def url(context: dict, name: str, **path_params: Any) -> str:
    request = context["request"]
    return request.url_for(name, **path_params)

def asset(context: dict, path: str) -> str:
    request = context["request"]
    return request.url_for('assets', path=path)
