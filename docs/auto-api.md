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


### Making Some Endpoints Public

If you want some auto API endpoints public and some private, even down to public GET vs POST you should keep the automatic CRUD scopes enabled and instead link UserID 1 (the anonymous user) to a role and link up the proper permissions for that role.  Public users are actually assigned a real uvicore user called anonymous, so user groups, roles and permissions apply to that public anonymous user just like any other user.



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

Notice these scopes apply to every single endpoint. User must be authenticated and have the `autoapi_user` permission.  They can hit ALL auto API endpoints with all HTTP verbs.

This is only handy if you want to give out ALL functionality to a set of users.  This is not a granular per HTTP verb approach.  To define a custom set of permissions for each HTTP verb use a scopes dictionary instead.  Like so


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

Although this is granular from an HTTP verb standpoint, it still applies to every single endpoint.

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

There are certain verbs which must NOT carry a body/payload.  Instead they act on a single resource defined in the URL.  These verbs are GET/HEAD/DELETE/OPTIONS.  Which means you can only DELETE a /{id} resource, never bulk with some sort of DELETE body payload.  Body in DELETE is technically allowed, but is generally ignored by clients, proxies and should not be used.  Get obviously has no body whatsoever, only URL and possibly queryParameters.

encode/httpx for example does not allow body data on GET/HEAD/DELETE/OPTIONS as expected.

Further, some verbs that do except body payload should still only ever act on a single resource defined in the url /{id}.  Like PUT.  PUT should never do bulk inserts.  PUT acts on a single resource to UPDATE that resource using the URL /{id}.  PUT can have a body/payload, which is the FULL resource to UPDATE.

At first I created my DELETE to accept

https://www.restapitutorial.com/lessons/httpmethods.html
PUT should be idempotent always, if it increments a counter, its NOT idempotent and POST should be used

GET
Has NO body/payload
/user       To get entire collection
/user/{id}  to get a single item
queryParams are OK on either / or /{id}

POST - creating, but also a catch-all verb
Has body/payload
/user           To create a new user (not idempotent), body can be one or many items
/user/delete    Custom, can have a body payload with complex query of WHAT to delete





https://stackoverflow.com/questions/299628/is-an-entity-body-allowed-for-an-http-delete-request
https://lists.w3.org/Archives/Public/ietf-http-wg/2020JanMar/0123.html
https://stackoverflow.com/questions/21863326/delete-multiple-records-using-rest




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
