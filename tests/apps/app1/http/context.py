"""
App1 custom Jinja template extras.

These demonstrate all four categories of custom template processors that a
Uvicore app can register via ``self.register_http_view_context_processors()``
in its provider (see ``app1/package/provider.py``):

    * context_functions - globals that receive the render context (``@pass_context``)
    * context_filters   - filters that receive the render context (``@pass_context``)
    * filters           - plain Jinja filters
    * tests             - Jinja tests usable as ``{% if x is <test> %}``

The framework itself registers ``url()``, ``asset()`` and ``public()`` as
context_functions (see ``uvicore/http/templating/context_functions.py``); these
are app-level additions layered on top.
"""
import math


def nav_active(context: dict, route_name: str, css_class: str = 'active') -> str:
    """context_function: return ``css_class`` when the current request is on ``route_name``.

    Used by the header/nav partial to highlight the active menu item, e.g.
    ``<a class="{{ nav_active('app1.about') }}" ...>``.  The engine wraps this
    with ``jinja2.pass_context`` so ``context`` is injected automatically.
    """
    request = context.get('request')
    if request is None:
        return ''
    try:
        target = request.url_for(route_name).path
    except Exception:
        return ''
    return css_class if request.url.path == target else ''


def money(context: dict, value) -> str:
    """context_filter: format a number as USD, e.g. ``{{ 1234.5 | money }}`` -> ``$1,234.50``."""
    try:
        return '${:,.2f}'.format(float(value))
    except (TypeError, ValueError):
        return str(value)


def shout(value) -> str:
    """filter (plain): uppercase and exclaim, e.g. ``{{ 'hello' | shout }}`` -> ``HELLO!``."""
    return '{}!'.format(str(value).upper())


def prime(n: int) -> bool:
    """test: usable as ``{% if n is prime %}``."""
    if not isinstance(n, int) or n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.isqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True
