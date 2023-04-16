# Setuptools Entrypoints

FIXME


Using `./uvicore` directly in app is good, but often we need actual setuptools entrypoints.

And sometimes those entrypoints might run a single click command, and sometimes they will will want to shoe an entire group.


Example of running a single click command
in pyproject.toml
```toml
[tool.poetry.scripts]
i3ctl = 'ohmyi3.commands.welcome:cli
```
This calls the regular stock welcome command


Example of building a custom click group and calling that instead
in pyproject.toml
```toml
[tool.poetry.scripts]
i3ctl = 'ohmyi3.commands.entrypoint:cli'
```

Create the custom `commands/entrypoing.py`

This boostraps uvicore and dynamically adds all of this main apps commands into a click group
specifically made for setup tools entrypoints


```python
import os
import sys
import uvicore
from uvicore.console import group
from ohmyi3.services import bootstrap
from uvicore.support.module import load

# Bootstrap the Uvicore application from the console entrypoint
app = bootstrap.application(is_console=True)

# Define a new asyncclick group
@group()
def cli():
    pass

# Dynamically add in all commands from this package matching this command_group
command_group='i3ctl'
package = uvicore.app.package(main=True);
if 'console' in package:
    if (package.registers.commands and uvicore.app.is_console):
        for key, group in package.console['groups'].items():
            if key == command_group:
                for command_name, command_class in group.commands.items():
                    cli.add_command(load(command_class).object, command_name)

# Instantiate the asyncclick group
try:
    cli(_anyio_backend='asyncio')
except KeyboardInterrupt:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
```

You have to `poetry install` each time you change an entrypoint location in pyproject.toml

Should be able to type `i3ctl` and see a list of further commands, like sync

`i3ctl welcome` - this works with asyncclick
`./uvicore i3ctl welcome` also works, because they are the same commands, just alternate entrypoint

