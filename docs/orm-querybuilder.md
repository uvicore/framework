# ORM Query Builder

Examples use a Uvicore model called `User`.

I also show the OpenAPI URL parameters used in the automatic model router.


## Find One

Find one user by primary key of 1.  Returns a single User instance, not a List.
```python
user = await User.query().find(1)
# URL: /users/1
```

Find one user by email.  Returns a single User instance, not a List.
```python
user = await User.query().find(email='mreschke@example.com')
# URL: /users?where={"email": "mreschke@example.com"}
```


## Get All

Get all users.  Returns a List of User instances.
```python
users = await User.query().get()
# URL: /users
```


## Where AND

!!! info
    Valid operators are `in, !in, like, !like, =, != >, >=, <, <=`.
    and `null` is a valid "value" (not operator), see null example below.

Get all users with eye_color red.  Operator is assumed `=`.
```python
users = await User.query().where('eye_color', 'red').get()
# URL: /users?where={"eye_color": "red"}
```

Explicit operator
2nd param is either the operator or the where value if operator is undefined.
```python
users = await User.query().where('eye_color', '=', 'red').get()
# URL: /users?where={"eye_color": ["=", "red"]}
```

Where In, Not In
```python
users = await User.query().where('eye_color', 'in', ['red', 'blue']).get()  # In
# URL: /users?where={"eye_color": ["in", ["red", "blue"]]}

users = await User.query().where('eye_color', '!in', ['red', 'blue']).get()  # Not in
# URL: /users?where={"eye_color": ["!in", ["red", "blue"]]}
```

Where Like, Not Like
```python
users = await User.query().where('eye_color', 'like', '%br%').get()  # Like
# URL: /users?where={"eye_color": ["like", "%br%"]}

users = await User.query().where('eye_color', '!like', '%br%').get()  # Not like
# URL: /users?where={"eye_color": ["!like", "%br%"]}
```

Where Null, Not Null
```python
users = await User.query().where('eye_color', 'null').get()  # Like
# URL: /users?where={"eye_color": "null"}

users = await User.query().where('eye_color', '!=', 'null').get()  # Not like
# URL: /users?where={"eye_color": ["!=", "null"]}
```

## Where OR

Where ORs are a bit limited at the moment.   The OR only works at the end of a where.  Meaning you cannot do complex (and (or) and (or)) order of operations

```python
users = await User.query().or_where([
    ('eye_color', 'red'),
    ('eye_color', 'blue')
]).get()
```

The or_where can be combined



## Where Multiples

There is a few ways to add multiple wheres.  You can either chain multiple `.where()` together, or use a single `.where()` with a `List of Tuples`.  The Tuple style accepts all the optional operators just like the normal `.where()`.

Multiple chains
```python
users = await User.query().where('eye_color', 'red').where('gender', '!=', 'male').get()
# URL: /users?where={"eye_color": "red", "gender": "male"}
```

List of Tuples
```python
users = await (User.query().where([
    ('eye_color', 'red'),
    ('gender', '!=', 'male'),
]).get()
```

