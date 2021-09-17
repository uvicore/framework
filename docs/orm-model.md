# ORM Model



## Tables

Most ORM models will have a corresponding database table (but they don't have to).  To define the table use the `__tableclass__` class variable to point to a proper uvicore table class.  If you want to inline your table definition you can do that as well.


If you have an actual uvicore table class, then simply point to that class using `__tableclass__`
```python
@uvicore.model()
class Post(Model['Post'], metaclass=ModelMetaclass):
    # Database table definition
    # Optional as some models have no database table
    __tableclass__ = table.Comments

    id: Optional[int] = Field('id', primary=True, read_only=True)
    slug: str = Field('unique_slug', required=True)
    title: str = Field('title', required=True)
    # ...
```


If you don't have a separate uvicore table class and you want to inline the table right in the model...
```python
@uvicore.model()
class Post(Model['Post'], metaclass=ModelMetaclass):
    __connection__ = 'wiki'
    __tablename__ =  'posts'
    __table__ = [
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('unique_slug', sa.String(length=100), unique=True),
        sa.Column('title', sa.String(length=100)),
        sa.Column('body', sa.Text()),
        sa.Column('other', sa.String(length=100), nullable=True),
        sa.Column('creator_id', sa.Integer, sa.ForeignKey(f"{users}.id"), nullable=False),
        sa.Column('owner_id', sa.Integer, sa.ForeignKey(f"{users}.id"), nullable=False),
    ]

    id: Optional[int] = Field('id', primary=True, read_only=True)
    slug: str = Field('unique_slug', required=True)
    title: str = Field('title', required=True)
    # ...
```

