# Routing


## New notes to move around

These are accurate

The auto model router already has `model.crud` style permissions attached and will require auth as long as you have some api auth middleware enabled.  If you have auth middleware enabled but you still want autoapi routes to be public, or to use a single permission, override it with the options argument on `.include()`

This will wipe out all scopes, meaning all auto endpoints are now PUBLIC
```python
# Include dynamic model CRUD API endpoints (the "auto API")!
# These routes are automatically protected by model.crud style permissions.
@route.group()
def autoapi():
    route.include(ModelRouter, options={
        'scopes': []
    })
```

This will set all to just 'authenticated', so the `model.crud` scopes are wiped out.
```python
# Include dynamic model CRUD API endpoints (the "auto API")!
# These routes are automatically protected by model.crud style permissions.
@route.group()
def autoapi():
    route.include(ModelRouter, options={
        'scopes': ['authenticated']
    })
```

This will append this scope to the existing auto `model.crud` scopes. And endpoints are only allows if user has ALL permissions, ie: both `['allowcrud', 'posts.read']` (unless your `admin`, it always wins)
```python
@route.group(scopes=['allowcrud'])
def autoapi():
    route.include(ModelRouter)
```










## OBSOLETE WARNING

This document is obsolete now that I refactored the entire routing infrastructure.

Obsolete below this line












## Routing Basics

Uvicore separates web and api routes into two files located in the `http/routes` directory.  These route files are loaded from your packages `Service Provider`. Dual routers allow for separate middleware and authentication mechanisms for web and api endpoints.  Route middleware and authentication is located in your packages `config/app.py` file.

All routes are defined inside the routes `register()` method. There are multiple ways to define route endpoints including method passing, decorators, groups and controllers.

**Basic Routing Example**
```python
import uvicore
from uvicore.http import response
from uvicore.http.routing import Routes, WebRouter

@uvicore.routes()
class Web(Routes):

    def register(self, route: WebRouter):
        """Register Web Route Endpoints"""

        # Define controller base path
        route.controllers = 'app.http.controllers'

        # Decorators
        @route.get('/users')
        def users():
            return response.Text('Route /usres here')

        # Passing in existing methods
        def posts():
            return response.Text('Route /posts here')
        route.get('/posts', posts)

        # Including controllers
        from app1.http.controllers.home import Home
        route.controller(Home)

        # Including controllers as strings using route.controllers path above
        route.controller('about')  # Assumes app1.http.controllers.home.Home class

        # If your controller has an __init__ with params
        route.controller('contact', options={'param': 'one'})

        # Groups as a Decorator
        @route.group(prefix='/admin')
        def admin():
            @route.get('/profile')
            def profile():
                return response.Text('Route /admin/profile here')

        # Groups as a List of existing methods
        # tokens and themes methods not defined for brevity
        route.group(prefix='/settings', routes=[
            route.get('/tokens', token_settings),
            route.get('/theme', theme_settings),
        ])

```


## Route Prefixes and Names

All routes are automatically given a route prefix which you define in `config/package.py`.  This prefix allows consuming developes of your package to alter each packages base URI to fit their needs.  For example, if you wrote a `wiki` app you probably want a simple `/` prefix for all routes.  If a developer consumes your wiki as a package inside their own app, they may override your wiki `config/package.py` and alter the prefix to `/wiki`.

Because of this route prefix, URL paths should never be referenced in views and controllers as they are subject to change and your links will break.  Instead you should always reference the `route name`.

All routes are automatically given a `route name`.  The name is based on your route path (naturally excluding your package wide prefix).  This name is also prefixed with your package name found in `config/package.py`.  For example `wiki.about`, `wiki.admin.profile`.

You can override the automatic name When defining routes, groups and controllers.  Prefixes can be defined on route groups and controllers.

```python
# Example app where config/package.py name='wiki'

# Default name based on the path
@route.get('/user/account')
def users():
    return response.Text('Name is wiki.user.account')

# Specifying a custom name
@route.get('/user/account', name='account')
def users():
    return response.Text('Name is wiki.account')

# Group default name based on path
@route.group(prefix='/admin')
def admin():
    @route.get('/profile')
    def profile():
        return response.Text('Name is wiki.admin.profile')

# Group with a custom name
@route.group(prefix='/admin', name='backend')
def admin():
    @route.get('/profile')
    def profile():
        return response.Text('Name is wiki.backend.profile')

# Controllers are by default not given a name prefix
# Assuming controller has a /home endpoint
@route.controller('home')  # name will be wiki.home

# Controllers with a prefix are given a name based on the prefix
# Assuming controller has a /home endpoint
@route.controller('home', prefix='my')  # name will be wiki.my.home

# Controllers with a custom name
# Assuming controller has a /home endpoint
@route.controller('home', name='our')  # name will be wiki.our.home
```


## Overriding Packages Routes

If you are consuming another developers package you may want to override some of their routes with your own.  For example, if you are building a CRM which includes another developers `blog` packages.  The `blog` packages has their own `/search` route which has a name of `blog.search`.  You want to write a custom CRM search page that overrides the blog search page.

Because all of your route names are automatically `prefixed` with your package name and because all route prefixes are automatically added with your package prefix, you must disable the auto-prefixer for the search route.  This will allow you to define the entire route path and name.

```python
# Your CRM package wants to override the blog packages search route
@route.get('/search', name='blog.search', autoprefix=False)
```
