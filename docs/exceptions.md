# Exceptions

In uvicore, Web and API endpoints are separated using two route engine.  Each engine has it's own set of middleware, exceptions and other configurations.  Because of this separation you can define exception handlers for each route engine in your `config/app.py` under `web.exceptions` and `api.exceptions`.


## API Exception Handler

The default uvicore API exception handler will show a basic JSON response using the proper HTTP response code

```json
{
  "status_code": 400,
  "message": "Bad Parameter",
  "detail": "Invalid order_by parameter, possibly invalid JSON?",
  "exception": "Expecting value: line 1 column 2 (char 1)",
  "extra": {
    "whatever": "you want here, its your dict"
  }
}
```

!!! warning "Debug Mode"
    If the raised exception provided an `exception=` parameter, the exception is ONLY added to the handler if `debug=True` is set in your `config/app.py` config.  These are usually the direct results of the `try...except` stack trace and will be stripped by uvicore for your safety while in production mode.  Never set `debug=True` in production!


To override the generic API handler, create your own method anywhere in your package, for example `exceptions/handlers.py`.  Then simply change your `config/app.py` `api.exceptions` to point to this new location.  You can see Uvicore's default exception handler by looking at the `uvicore.http.exceptions.handlers.api` method.  Something like this:

```python
from uvicore.http import response
from uvicore.http import Request
from starlette.exceptions import HTTPException

async def api(request: Request, e: HTTPException) -> response.JSON:
    """Main exception handler for all API endpoints"""

    # Get error payload (smart based on uvicore or starlette HTTPException)
    (status_code, detail, message, exception, extra, headers) = _get_payload(e)
    return response.JSON(
        {
            "status_code": status_code,
            "message": message,
            "detail": detail,
            "exception": exception,
            "extra": extra,
        }, status_code=status_code, headers=headers
    )
```


## Web Exception Handler

The default Web exception handler will attempt to locate and render a `Jinja2` template with the same name as the `status_code` inside a `errors` view folder.  For example a `404` error will try to render the `errors/404.j2` template.  If the template does not exist [in ANY package] it will then attempt to locate and render the `errors/catch_all.j2` template.  If that templates does not exist in any package it will return a basic HTML page with the error details.  By creating these templates, you have complete control over each individual error including a custom catch all!

To create custom error pages, there is no need to touch `config/app.py` `web.exceptions` config option.  Instead simply create a `http/views/errors/404.j2` and `http/views/errors/catch_all.j2` file in your package and the default Web exception handler will return your new template.  All packages "view paths" are combined and merged.  This means if packageA had a custom `errors/404.j2` and your running app didn't, it would use packageA.  If you created the `errors/404.j2`, your package would win since it is always defined last.  Everything in Uvicore can be overridden, configs, assets, templates, connections etc... Last package defined generally wins in all override battles.

The `Jinja2` variables available to you in these custom error template are
```
{{ request }}
{{ status_code }}
{{ message }}
{{ detail }}
{{ exception }} - will always be blank if debug=False
{{ extra }} - a user defined custom dictionary
```
