import uvicore
from uvicore.console import command, argument, option
from uvicore.support.dumper import dd, dump


@command()
@option('--raw', is_flag=True, help='Show output without prettyprinter')
def bindings(raw: bool = False):
    """List all Ioc Bindings"""
    if not raw:
        uvicore.log.header("List of all Ioc bindings")
        uvicore.log.line()
        dump(uvicore.ioc.bindings)
    else:
        dic = {}
        for key, binding in uvicore.ioc.bindings.items():
            dic[key] = binding.__dict__
        print(dic)


@command()
def singletons():
    """List Singleton Ioc Bindings"""
    uvicore.log.header("List of all Ioc singleton bindings")
    uvicore.log.line()
    bindings = {key:binding for (key, binding) in uvicore.ioc.bindings.items() if binding.singleton == True}
    dump(bindings)


@command()
@argument('type')
def type(type: str):
    """List Ioc Bindings of a Specific Type (comma separated)"""
    uvicore.log.header("List of all {} Ioc bindings".format(type))
    uvicore.log.line()

    types = []
    if ',' in type:
        parts = type.split(',')
        for part in parts:
            types.append(part.upper())
    else:
        types = [type.upper()]

    bindings = {}
    for key, binding in uvicore.ioc.bindings.items():
        if binding.type.upper() in types:
            bindings[key] = binding
    #bindings = {key:binding for (key, binding) in uvicore.ioc.bindings.items() if binding.type.upper() == type}
    dump(bindings)


@command()
def overrides():
    """List Overridden Ioc Bindings"""
    uvicore.log.header("List of all Ioc bindings that have been overridden")
    uvicore.log.line()
    bindings = {key:binding for (key, binding) in uvicore.ioc.bindings.items() if binding.path != key}
    # overridden = {}
    # for key, binding in uvicore.ioc.bindings.items():
    #     if key != binding.path:
    #         overridden[key] = binding
    dump(bindings)


@command()
@argument('key', default='')
@option('--raw', is_flag=True, help='Show output without prettyprinter')
def get(key: str = None, raw: bool = False):
    """Get a binding by name"""
    if not raw:
        dump(uvicore.ioc.binding(key))
    else:
        print(uvicore.ioc.binding(key).__dict__)
