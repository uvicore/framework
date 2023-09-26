import uvicore
import json as JSON
from uvicore.typing import Dict
from uvicore.console import command, argument, option
from uvicore import app, log
from uvicore.support.dumper import dd, dump

# Commands
# list = typer.Typer()
# show = typer.Typer()
# providers = typer.Typer()


@command()
def list():
    """List all packages"""
    log.header("List of all Packages (in exact order of registration dependency)")
    log.line()
    dump(app.packages)
    # for package in app.packages.values():
    #     dump("Package: " + package.name)
    #     dump(package)
    #     print()
        #dump(f"== {package.name} deep merged configs --")
        #dump(package.config())


@command()
@argument('package')
def get(package: str):
    """Show detailed info for one package"""
    if package == 'main':
        pkg = app.package(main=True)
    else:
        pkg = app.package(package)

    if pkg:
        log.header("Package object for " + package)
        log.line()
        dump(pkg)
        print()

        #log.header("Deep merged configs for " + package)
        #log.line()
        #dump(pkg.config())
    else:
        exit(f"Package {package} not found")

@command()
@option('--json', is_flag=True, help='Show providers as JSON')
def providers(json: bool):
    """Show providers graph"""
    if json:
        # This json stuff is just experimantal junk
        print(JSON.dumps(app.providers))
    else:
        log.header("Package provider graph (in exact order of registration dependency)")
        log.line()
        dump(app.providers)

        log.nl()
        log.line()
        log.header("Package providers as seen from the Ioc")
        bindings = {key:binding for (key, binding) in uvicore.ioc.bindings.items() if binding.type.lower() == 'provider'}
        dump(bindings)


