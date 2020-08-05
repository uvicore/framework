# Configuration

Configuration is a Service Provider that adds config and settings capability
to uvicore packages.

This services is fired up as a dependency in `foundation/config/package.py`.

The Ioc binding `Configuration` is a Singleton bound from the service provider
`register()` method.  The singleton is saved to `uvicore.config` and also in the
main `uvicore.app` global for use in two different ways.


## Registering Configs

All packages can register their own configs using a unique `key`.  This
registraion is done inside the packages service provider `register()` method.
If a config is already registered with the same `key` then the Dictionary value
will be "deep merged".  This allows packages to override other package configs
at a granular level.  The last provider defined wins in an override battle.

In a provider, `self.name` is the name of you package, ie: `mreschke.wiki`.  In
this example I am also overriding the `uvicore.foundation` config with my own
partial config that gets deep merged.

```python
class Wiki(ServiceProvider):

    def register(self) -> None:
        # Register configs
        # If config key already exists items will be deep merged allowing
        # you to override small peices of other package configs
        self.configs([
            # Here self.name is your packages name (ie: mreschke.wiki).
            {'key': self.name, 'module': 'mreschke.wiki.config.wiki.config'},

            # Foundation exists, so this is a deep merge override
            {'key': 'uvicore.foundation', 'module': 'mreschke.wiki.config.uvicore.foundation.config'},
        ])
```

Because of this merging technology you can split out your `config/wiki.py` file
into many files if you wish.  Maybe one for `config/database.py` for example.
If that file had a `database: {...}` dictionary it would be merge into your wiki
config by adding this to your `register() self.config` list.
```python
{'key': self.name, 'module': 'mreschke.wiki.config.database.config'}
```



## Getting a Config Instance

You can get hold of the main config instance in many different ways.

By importing the `uvicore` module as a namespace and accessing the config global
variable
```python
import uvicore
uvicore.config('app.name')
```

By importing the `uvicore.config` global variable directly
```python
from uvicore import config
config('app.name')
```

By importing the main `uvicore.app` global variable which has a config property
for your convenience.  Often times you will already have `app` imported for
other needs.
```python
from uvicore import app
app.config('app.name')

# Of course this works too
import uvicore
uvicore.app.config('app.name')
```

By "making" from the Ioc container
```python
import uvicore
config = uvicore.ioc.make('config')  # Other aliases: Configuration, Config
config('app.name')
```


## Usage

!!! info
    `config` is a class with a `__call__` method so you can use the class like a
    method `config('app.name')`.  This is provided as a convenience.
    Under the hood the `__call__` simply calls a `get()` method.  Technically you
    can also get config values by using this `get()` method like so
    `config.get('app')`.


### Getting Values

Get the entire config Dictionary from all packages, completely deep merged based
on provider order override
```python
config()
```

Get the main `app config` which is defined in the main running app
`config/app.py` file.  This main app config is not deep merged as it is the only
running app config.
```python
config('app')
```

Get a value from the app config
```python
config('app.name')
config('app.server.port')
```

Get the entire config for a package named `mreschke.wiki` and get a few single
values.  This is the main wiki config defined in `config/wiki.py` for example.
This config is meant to be overridden as needed by other packages.
```python
config('mreschke.wiki')
config('mreschke.wiki.database.connections')
```

All packages have a `config/package.py`.  This config is not deep merged as the
settings here should never be overridden.  This package config is added to your
main packages config (for example in `config/wiki.py`) under the `package` key.
```python
config('mreschke.wiki.package.name')
```

### Settings Values

You can set values by completely overriding the value using `set()` or by
deep merging with existing values using `merge()`

**Sets** the entire database connection dictionary with a new one
```python
config.set('mreschke.wiki.database.connections', '{...}')
```

**Merges** this database connection dictinoary with one that already exists
```python
config.merge('mreschke.wiki.database.connections', '{...}')
```
