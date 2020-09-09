# Pydantic Hack

Current pydantic version: 1.6.1

Always import pydantic from `uvicore.support.pydantic`

I hacked the `main.py` file to use my `utils.validate_field_name`

Because upstream does not allow shadowing (_Model classmethod with same name as a field).

Which is not good for an ORM.  I want .find, .get, .where etc... but what if the
user wants a field called `find` or `get`.  Now they can.

Note however they can NOT have fields of `save` or `delete` since those are
instance properties that must exists.
