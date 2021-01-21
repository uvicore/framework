from typing import Any


def url(context: dict, name: str, **path_params: Any) -> str:
    request = context["request"]
    return request.url_for(name, **path_params)
