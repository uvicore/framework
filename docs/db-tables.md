# Database Tables


Uvicore provides two methods to define your SQLAlchemy tables.


## As Separate Files

Tables may be stored in separate files located in `database/tables/*`.  You may use the Uvicore schematic generator to create this table automatically, or create it by hand.



```bash
./uvicore gen table --help
./uvicore gen table posts
```

!!! warning "init file"
    Be sure to add your new table to the `database/tables/__init__.py`

The schematic includes many commented examples of how to use the table, a sort of auto-documentation.

A basic `posts` table looks like this
```python
import uvicore
import sqlalchemy as sa
from uvicore.database import Table
from uvicore.support.dumper import dump

# Get related tablenames with proper prefixes
users = uvicore.db.tablename('auth.users')

@uvicore.table()
class Posts(Table):

    # Actual database table name
    # Plural table names and singluar model names are encouraged
    # Do not add a package prefix, leave that to the connection config
    name = 'posts'

    # Connection for this database from your config file
    connection = 'yourapp'

    # SQLAlchemy Table definition as a list (exclude name and metadata)
    # This will be converted into an actual SQLAlchemy Table() instance
    # See https://docs.sqlalchemy.org/en/13/core/schema.html
    schema = [
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('unique_slug', sa.String(length=100), unique=True),
        sa.Column('title', sa.String(length=100)),
        sa.Column('body', sa.Text()),
        sa.Column('other', sa.String(length=100), nullable=True),
        sa.Column('creator_id', sa.Integer, sa.ForeignKey(f"{users}.id"), nullable=False),
        sa.Column('owner_id', sa.Integer, sa.ForeignKey(f"{users}.id"), nullable=False),
    ]

    # Optional SQLAlchemy Table() instance kwargs
    schema_kwargs = {
        #'sqlite_autoincrement': True,
    }
```

!!! tip
    In general, tables should be plural (posts) while their corresponding ORM model (if you decide to use the ORM) would be singular (post).  This is a convention rather than a rule.


If you are using the Uvicore ORM (optional as the database stands alone as a query builder only), and you are defining your table in a separate file, simply point the `__tableclass__` to the proper table class.

```python
# ...
from yourname.yourapp.database.tables import posts as table

@uvicore.model()
class Post(Model['Post'], metaclass=ModelMetaclass):
    """Yourapp Posts"""

    # Database table definition
    # Optional as some models have no database table
    __tableclass__ = table.Posts

    #...
```


## As ORM Model Inline

If you are using the Uvicore ORM (optional as the database stands alone as a query builder only), and you want to define your tables inline instead of in a separate file, you may do so like this:

```python
# ...
from yourname.yourapp.database.tables import posts as table

@uvicore.model()
class Post(Model['Post'], metaclass=ModelMetaclass):
    """Yourapp Posts"""

    # Database table definition
    # Optional as some models have no database table
    __connection__ = 'yourapp'
    __tablename__ = 'posts'
    __table__ = [
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('unique_slug', sa.String(length=100), unique=True),
        sa.Column('title', sa.String(length=100)),
        sa.Column('body', sa.Text()),
        sa.Column('other', sa.String(length=100), nullable=True),
        sa.Column('creator_id', sa.Integer, sa.ForeignKey(f"{users}.id"), nullable=False),
        sa.Column('owner_id', sa.Integer, sa.ForeignKey(f"{users}.id"), nullable=False),
    ]
    #...
```

!!! warning "init file"
    Be sure to add your models to the `models/__init__.py`

See the ORM documentation for more ORM specific details.
