# Exceptions

In uvicore, Web and API endpoints are separated using two route engine.  Each engine has it's own set of middleware, exceptions and other configurations.  Because of this separation you can define exception handlers for each route engine in your `config/app.py` under `web.exceptions` and `api.exceptions`.


## API Exception Handler

The default API exception handler will simply show a basic JSON response with message using the proper HTTP response code

```json
{
    "message": "Not Found - Custom Text here"
}
```

To override the generic API handler, create your own method anywhere in your package, for example `exceptions/handlers.py`.  Then simply change your `config/app.py` `api.exceptions` to point to this new location.  You can see Uvicore's default exception handler by looking at the `uvicore.http.exceptions.handlers.api` method.  Something like this:

```python
from uvicore.http import response
from uvicore.http import Request
from starlette.exceptions import HTTPException

async def api(request: Request, e: HTTPException) -> response.JSON:
    """Main exception handler for all API endpoints"""

    # Defined in the running app config api.exceptions.main
    headers = getattr(e, "headers", None)
    return response.JSON(
        {"message": e.detail}, status_code=e.status_code, headers=headers
    )
```


## Web Exception Handler

The defailt Web exception handler will attempt to return a Jinja2 template at the `errors/404.j2` location.  Where `404` is the specific error status code.  If the template does not exist it will simply return a basic HTML page with the error details.

To create custom error pages, there is no need to touch `config/app.py` `web.exceptions` config option.  Instead simply create a `http/views/errors/404.j2` file in your package and the default Web exception handler will return that template.
