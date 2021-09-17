# Database Configuration

Uvicore utilizes [encode/databases](https://github.com/encode/databases) as an async adapter for [SQLAlchemy Core](https://docs.sqlalchemy.org/en/13/core/tutorial.html) (core is the query builder only, NO SQLAlchemy ORM).  This was in place before SQLAlchemy 1.4 came out, which is now async.  At some point Uvicore will be updated to remove the `encode/databases` dependency.  Keep in mind that Uvicore does NOT utilize SQLAlchemy for an ORM as Uvicore has a custom [Pydantic](/orm-pydantic/) based ORM that is more fluent and elegant.

Because Uvicore database utilizes [SQLAlchemy Core](https://docs.sqlalchemy.org/en/13/core/tutorial.html), Uvicore supports any database engine that SQLAlchemy supports including MySQL, PostgreSQL, MSSQL etc...


## Dependency

In order to use the database layer with Uvicore you must first ensure you have installed the `database` extras from the framework.  This is by default already included in the `uvicore-installer`.
```
# Poetry pyproject.toml
uvicore = {version = "0.1.*", extras = ["database", "redis", "web"]}

# Pipenv Pipfile
uvicore = {version = "==0.1.*", extras = ["database", "redis", "web"]}

# requirements.txt
uvicore[database,redis,web] == 0.1.*
```

After the database extras have been installed you must update your `config.package.py` `dependencies` OrderedDict in `config/package.py`
```python
    'dependencies': OrderedDict({
        'uvicore.foundation': {
            'provider': 'uvicore.foundation.services.Foundation',
        },
        # ...
        'uvicore.database': {
            'provider': 'uvicore.database.services.Database',
        },
        # ...
    }),
```

Notice the ORM dependency does not need to be defined.  Uvicore can use a raw query builder level database access layer without an ORM.


## Connection Strings

Uvicore uses your `config/package.py` configuration file to store connection strings. Add the proper connection, be sure to use the `.env` file along with the `env()` helper to keep your secrets out of git.

```python

config = {
    # ...
    'database': {
        'default': env('DATABASE_DEFAULT', 'yourapp'),
        'connections': {
            # SQLite Example
            # 'yourapp': {
            #     'driver': 'sqlite',
            #     'database': ':memory',
            #     'prefix': None,
            # },

            # MySQL Example
            'yourapp': {
                'driver': env('DB_YOURAPP_DRIVER', 'mysql'),
                'dialect': env('DB_YOURAPP_DIALECT', 'pymysql'),
                'host': env('DB_YOURAPP_HOST', '127.0.0.1'),
                'port': env.int('DB_YOURAPP_PORT', 3306),
                'database': env('DB_YOURAPP_DB', 'yourapp'),
                'username': env('DB_YOURAPP_USER', 'yourdbuser'),
                'password': env('DB_YOURAPP_PASSWORD', 'password'),
                'prefix': env('DB_YOURAPP_PREFIX', None),
            },
        },
    },
    # ...
}
```
!!! note
    The reason this is stored in `config/package.py` instead of `config/app.py` is because `config/package.py` is meant to be overridden by any developer consuming your app as a package inside their own app.  The package consumer gets to change where your package stores data.  Devs can also override using their `.env` file so be sure to use `env('XYZ')` in your configs.

From the [Uvicore CLI](/cli/), you can see all deeply merged connection strings for your app and any Uvicore package dependencies that use the DB by running
```bash
./uvicore db connections
```
