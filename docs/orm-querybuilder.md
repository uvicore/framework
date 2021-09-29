# ORM Query Builder

Examples use a Uvicore model called `User` and `Post`.

I also show the API URL parameters used in the automatic model router.


## Find One

Find one user by primary key of 1.  Returns a single User model instance, not a List.
```python
user = await User.query().find(1)
# URL: /users/1
```

Find one user by email.  Returns a single User model instance, not a List.  If this happens to return multiple results from the Database, TOP 1 is returned, never a List.
```python
user = await User.query().find(email='mreschke@example.com')
# URL: /users?where=["email","mreschke@example.com"]
```

!!! tip
    `.find()` ignores any `.where()`, `.or_where()`, `.order_by()`, `.key_by()` as those do not apply to finding a single record.





## Get All

Get all users.  Returns a List of User model instances.
```python
users = await User.query().get()
# URL: /users
```





## Where


!!! note "Operators"
    Valid operators are `in, !in, like, !like, =, != >, >=, <, <=`.
    and `'null'` (in quotes) is a valid "value" (not operator), see null example below.

Get all users with eye_color blue.  Operator is assumed `=`.
```python
users = await User.query().where('eye_color', 'blue').get()
# URL: /users?where=["eye_color","blue"]
```

Explicit operator
2nd param is either the operator or the where value if operator is undefined.
```python
users = await User.query().where('eye_color', '=', 'blue').get()
# URL: /users?where=["eye_color","=","blue"]
```

Where In, Not In
```python
users = await User.query().where('eye_color', 'in', ['green', 'blue']).get()  # In
# URL: /users?where=["eye_color","in",["green", "blue"]]

users = await User.query().where('eye_color', '!in', ['green', 'blue']).get()  # Not in
# URL: /users?where=["eye_color","!in",["green", "blue"]]
```

Where Like, Not Like
```python
users = await User.query().where('eye_color', 'like', '%br%').get()  # Like
# URL: /users?where=["eye_color","like","%br%"]

users = await User.query().where('eye_color', '!like', '%br%').get()  # Not like
# URL: /users?where=["eye_color","!like","%br%"]
```

Where Null, Not Null
```python
users = await User.query().where('eye_color', 'null').get()  # Like
# URL: /users?where=["eye_color","null"]

users = await User.query().where('eye_color', '!=', 'null').get()  # Not like
# URL: /users?where=["eye_color","!=","null"]
```



### Where OR

Where ORs are a bit limited at the moment.   The OR only works at the end of a where in the final SQL statement.  Meaning you cannot do complex (and (or) and (or)) order of operations

```python
users = await User.query().or_where([
    ('eye_color', 'green'),
    ('eye_color', '=', 'blue')
]).get()
# URL: /users?or_where=[["eye_color","green],["eye_color","=","blue"]]
# SQL: SELECT * FROM User WHERE eye_color='green' OR eye_color='blue'
```

The `or_where` can be combined with `where` and any other query builder method
```python
users = await (User.query()
    .where('gender', 'male')
    .where('hair_color', 'blonde')
    .or_where([
        ('eye_color', 'green'),
        ('eye_color', 'blue')
    ]
).get())
# URL: /users?where=[["gender","male"],["hair_color", "blonde"]]&or_where=[["eye_color","green"],["eye_color","blue"]]
# SQL: SELECT * FROM User WHERE gender='male' AND hair_color='blonde' AND (eye_color='green' OR eye_color='blue')
```




### Where Multiples

There is a few ways to add multiple wheres.  You can either chain multiple `.where()` together, or use a single `.where()` with a `List of Tuples`.  The Tuple style accepts all the optional operators just like the normal `.where()`.

Multiple chains
```python
users = await User.query().where('eye_color', 'green').where('gender', '!=', 'male').get()
# URL: /users?where=[["eye_color","green"],["gender","!=","male"]]
```

List of Tuples
```python
users = await (User.query().where([
    ('eye_color', 'green'),
    ('gender', '!=', 'male'),
]).get()
# URL: /users?where=[["eye_color","green"],["gender","!=","male"]]
```



## Include Relations

You can include child relations of any relational type by using `include()`

`include()` can take infinite parameters or a List
```python
# Infinite parameters
posts = await Post.query().include('creator', 'comments').get()
# URL:  /posts?include=creator,comments
# URL2: /posts?include=creator&include=comments

# As a List
posts = await Post.query().include(['creator', 'comments']).get()
# URL:  /posts?include=creator,comments
# URL2: /posts?include=creator&include=comments
```

You can include any number of deeply nested relations using dot notation.  Assume the posts `creator` links to the `User` model.  Further the `User` model has a `info` one-to-one.
```python
posts = await Post.query().include('creator.info', 'comments.creator', 'tags').get()
# URL:  /posts?include=creator.info,comments.creator,tags
# URL2: /posts?include=creator.info&include=comments.creator&include=tags
```

Most other query builder methods on relations use dot notation as well.
```python
posts = (await Post.query()
    .include('creator.info', 'comments.creator')
    .where('deleted', False)
    .where('creator.info.title', 'Master Gardner')
    .filter('comments.deleted', False)
    .sort('comments.created_at', 'DESC'),
    .order_by('created_at')
    .get()
)
```



!!! info
    All relations in a dot notation will be included, so `creator.info` includes both creator `User` and the `Info` of that creator.  No need to specify twice as `['creator', 'creator.info']`
