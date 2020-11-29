import uvicore
from uvicore.console import command, argument
from uvicore.support.dumper import dd, dump


@command()
def bindings():
    """List all Ioc Bindings"""
    uvicore.log.header("List of all Ioc bindings")
    uvicore.log.line()
    dump(uvicore.ioc.bindings)


@command()
def singletons():
    """List all Ioc Bindings Singletons"""
    uvicore.log.header("List of all Ioc singleton bindings")
    uvicore.log.line()
    bindings = {key:binding for (key, binding) in uvicore.ioc.bindings.items() if binding.singleton == True}
    dump(bindings)


@command()
@argument('type')
def type(type: str):
    """List all Ioc Bindings of a Specific Type"""
    type = type.upper()
    uvicore.log.header("List of all {} Ioc bindings".format(type))
    uvicore.log.line()
    bindings = {key:binding for (key, binding) in uvicore.ioc.bindings.items() if binding.type.upper() == type}
    dump(bindings)


@command()
def overrides():
    """List all Ioc Bindings That Have Been Overridden"""
    uvicore.log.header("List of all Ioc bindings that have been overridden")
    uvicore.log.line()
    bindings = {key:binding for (key, binding) in uvicore.ioc.bindings.items() if binding.path != key}
    # overridden = {}
    # for key, binding in uvicore.ioc.bindings.items():
    #     if key != binding.path:
    #         overridden[key] = binding
    dump(bindings)
