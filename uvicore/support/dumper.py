import prettyprinter

# Enable extras like @dataclass
prettyprinter.install_extras(exclude=['django', 'ipython_repr_pretty', 'ipython'])

def dump(*args):
    """Dump variables using prettyprinter"""
    for arg in args:
        prettyprinter.cpprint(arg)


def dd(*args):
    """Dump variables using prettyprinter and exit()"""
    for arg in args:
        prettyprinter.cpprint(arg)
    exit()
