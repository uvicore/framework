import prettyprinter
from prettyprinter import *

# Enable extras like @dataclass
prettyprinter.install_extras(exclude=[
     # Not using django, no need to print django models
    'django',

    'numpy',

    # Maybe when I get a shell ?
    'ipython_repr_pretty',
    'ipython',
    'attrs',
])
