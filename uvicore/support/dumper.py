import prettyprinter

# Enable extras like @dataclass
prettyprinter.install_extras(exclude=[
     # Not using django, no need to print django models
    'django',

    # Maybe when I get a shell ?
    'ipython_repr_pretty',
    'ipython',
    'attrs',
])

def dump(*args):
    """Dump variables using prettyprinter"""
    for arg in args:
        prettyprinter.cpprint(arg)


def dd(*args):
    """Dump variables using prettyprinter and exit()"""
    for arg in args:
        prettyprinter.cpprint(arg)
    exit()
