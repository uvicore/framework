import json as JSON
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
    log.header("List of all Packages (in exact order of registration dependency)").line()
    dump(app.packages)
    # for package in app.packages.values():
    #     dump("Package: " + package.name)
    #     dump(package)
    #     print()
        #dump(f"== {package.name} deep merged configs --")
        #dump(package.config())


@command()
@argument('package')
def show(package: str):
    """Show detailed info for one package"""
    if package == 'main':
        pkg = app.package(main=True)
    else:
        pkg = app.package(package)

    if pkg:
        log.header("Package object for " + package).line()
        dump(pkg)
        print()
        log.header("Deep merged configs for " + package).line()
        dump(pkg.config())
    else:
        exit(f"Package {package} not found")

@command()
@option('--json', is_flag=True, help='Show providers as JSON')
def providers(json: bool):
    """Show providers graph"""
    if json:
        print(JSON.dumps(app.providers))
    else:
        log.header("Package provider graph (in exact order of registration dependency)").line()
        for (name, detail) in app.providers.items():
            log.info(name)
            dump(detail)
            print()
