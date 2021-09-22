# ORM Model


## Summary

About ORM models




## OpenDocs Example Override

The OpenAPI docs will provide an automatic example for request and response results based on your model schema.  You can override this default example by leveraging the [Pydantic](/orm-pydantic/) inheritance of your ORM models.  Pydantic provides a `Config` class with a `schema_extra.example` section.

```python
@uvicore.model()
class Post(Model['Post'], metaclass=ModelMetaclass):
    """Yourapp Posts"""

    # Pydantic configuration override
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "slug": "title-as-a-slug",
                #...
            },
        }
    #...
```




## Tables

Most ORM models will have a corresponding database table (but they don't have to).  To define the table use the `__tableclass__` class variable to point to a proper uvicore table class.  If you want to inline your table definition you can do that as well.  See [Database Tables](/db-tables) for more information.



## Tableless

ORM models do not require a corresponding database table.

  Perhaps you are creating an API passthrough with a custom schema or
