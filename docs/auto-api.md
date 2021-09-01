# Auto API


Uvicore has an automatic CRUD Model Router for API usage which can be enabled in your `http/routes/api.py` like so

```python
# http/routes/api.py
def register(self, route: ApiRouter):
    # ...

    # Include dynamic model CRUD API endpoints (the "auto API")!
    # These routes are automatically protected by model.crud style permissions.
    route.include(ModelRouter)

    # ...
```

For every uvicore model, multiple API endpoints are automatically created to perform CRUD operations on the list of models via `/users` or a single model via `/users/{id}`.  You can see these new routes when viewing the OpenAPI doc endpoint at `http://localhost:5000/api/docs`


## Permissions

When a uvicore model is created, a set of `model.crud` style permissions are automatically generated and stored in the `permissions` database table.  For example

| entity      | name        |
| ----------- | ----------- |
| users       | users.create|
| users       | users.read  |
| users       | users.update|
| users       | users.delete|

When visiting `GET` `http://localhost:5000/api/users` the user must have the `users.read` scope.  Scopes are the same as these permission strings.

!!! note
    Permissions and Scopes are the same thing.  You limit all endpoints using the `scopes=[]` List which are linked to the `user/groups/roles` in the database as `permissions`.

Each auto API endpoint is limited by the proper scope.

- `HTTP GET` requires the `users.read` scope.
- `HTTP POST` requires the `users.create` scope.
- `HTTP PUT` requires the `users.update` scope.
- `HTTP PATCH` requires the `users.update` scope.
- `HTTP DELETE` requires the `users.delete` scope.


### Make it all Public

If you wanted ALL auto API endpoints to be wide open to the public, with no limiting scopes (permissions) at all, use the `options` parameter and set the `scopes` key to a blank List.

```python
# http/routes/api.py
def register(self, route: ApiRouter):
    # ...

    # Include dynamic model CRUD API endpoints (the "auto API")!
    # These routes are automatically protected by model.crud style permissions.
    route.include(ModelRouter, options={
        'scopes': []
    })

    # ...
```

!!! tip
    Although the auto API endpoints now have no scopes themselves, they still obey any higher order `scopes` you may have defined in your top level router or controller files.


### Custom scopes without CRUD scopes

If you wanted to remove the automatic CRUD scopes (permissions) from all auto API endpoints and instead define your own List of scopes for all endpoints.

```python
# http/routes/api.py
def register(self, route: ApiRouter):
    # ...

    # Include dynamic model CRUD API endpoints (the "auto API")!
    # These routes are automatically protected by model.crud style permissions.
    route.include(ModelRouter, options={
        'scopes': ['authenticated', 'autoapi_user']
    })

    # ...
```
User must be authenticated and have the `autoapi_user` permission.  They can hit ALL auto API endpoints with all HTTP verbs.

This is only handy if you want to give out ALL functionality to a set of users.  This is not a granular per HTTP verb approach.  To define a custom set of permissions for each HTTP verb use a scopes dictionary instead.


```python
# http/routes/api.py
def register(self, route: ApiRouter):
    # ...

    # Include dynamic model CRUD API endpoints (the "auto API")!
    # These routes are automatically protected by model.crud style permissions.
    route.include(ModelRouter, options={
        'scopes': {
            'create': ['autoapi.create'],
            'read': ['autoapi.read'],
            'update': ['autoapi.update'],
            'delete': ['autoapi.delete'],
        }
    })

    # ...
```



!!! tip
    Any higher order `scopes` defined in top level routes or controllers are also obeyed


### Extend existing CRUD scopes

If you wanted to extend/append your own scopes to the existing automatic `model.crud` styles scopes, wrap it in a `@route.group` decorator

```python
# http/routes/api.py
def register(self, route: ApiRouter):
    # ...

    # Include dynamic model CRUD API endpoints (the "auto API")!
    # These routes are automatically protected by model.crud style permissions.
    @route.group(scopes=['authenticated', 'autoapi_user']):
    def autoapi():
        route.include(ModelRouter)

    # ...
```
Now a user must have the actual CRUD scope (ex: `users.read`) and also the `authenticated` and `autoapi_user` scope.

!!! tip
    Any higher order `scopes` defined in top level routes or controllers are also obeyed





## Notes

Notes from within the model_router.py, moved here


**REST Notes**
```
https://www.mscharhag.com/p/rest-api-design
https://www.mscharhag.com/api-design/http-post-put-patch

GET
HEAD
OPTIONS
TRACE


POST is for new records
    POST /spaces
    Not idempotent as it will continue to create new resources
    If new post, return 200
    If endpoint has no response but created, return 204 (no content but success)

PUT is for updating existing records whos ID is in the url
    PUT /spaces/123
    Not for partial updates, expects the FULL object
    Idempotent

PATCH
    PATCH /spaces/123
    Like PUT, but can be partial object, or could be full, either way
    Updates only records defined in the partial object
    {
        'creator': 4
    }

    BULK updates?
    PATCH /spaces?where={"something": "other"}
    Takes a partial JSON blob, with the data you want to update in BULK
    {
        'something': 'new',
        'title': 'all get the same title'
    }

DELETE
    DELETE /spaces/123
    Deletes one space by ID
    maybe a new permission string spaces.update_bulk?

    BULK?
    DELETE /spaces?where={"creator_id": 1}
    maybe a body with confirm code?
    {
        env API_BULK_DELETE_CODE: 1234123412341234123412341234
        confirm: yes sir code 123423412341234
    }
    or maybe a new permission string, spaces.delete_bulk?

```


**URL query notes**
```
Include
-------
include=sections.topics

Where AND
----------
where={"id": 1}
where={"id": 1, "name": "test"}

where={"id": [">", 1]}

where={"id": ["in", ["one", "two"]]}
where={"id": [">", 5], "name": "asdf", "email": ["like", "asdf"]}


Where OR
--------
or_where=(id,1)+(id,3)

Group By
--------

Order By
--------
order_by=[{"id": "ASC"}, {"name": "DESC"}]

Paging
------
page=1
size=10
translates to ORM limit and offset

Cache
-----
cache=60  in seconds
```
