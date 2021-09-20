# ORM Model


## Summary

About ORM models







## Tables

Most ORM models will have a corresponding database table (but they don't have to).  To define the table use the `__tableclass__` class variable to point to a proper uvicore table class.  If you want to inline your table definition you can do that as well.  See [Database Tables](/db-tables) for more information.



## Tableless

ORM models do not require a corresponding database table.

  Perhaps you are creating an API passthrough with a custom schema or
