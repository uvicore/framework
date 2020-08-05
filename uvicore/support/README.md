# Uvicore Support

Support is another term for Helpers, Tools or Utilities.  These
are single modules that help perform a stand alone function.

There are no service providers here.

Do not create a __init__.py for an index.  Use the module as a namespace
or import the method directly.

```python
from uvicore.support import module
module.load(...)

from uvicore.support.dumper import dump, dd
dd(...)
```
