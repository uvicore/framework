import typer
import json as JSON
from uvicore import app, log
from uvicore.support.dumper import dd, dump

# Commands
list = typer.Typer()
show = typer.Typer()
providers = typer.Typer()


@list.command()
def list_cmd():
    """List all packages"""
    log.header("List of all Packages (in exact order of registration dependency)").line()
    dump(app.packages)
    # for package in app.packages.values():
    #     dump("Package: " + package.name)
    #     dump(package)
    #     print()
        #dump(f"== {package.name} deep merged configs --")
        #dump(package.config())


@show.command()
def show_cmd(package: str):
    """Show detailed info for one package"""
    if package == 'main':
        pkg = app.package(main=True)
    else:
        pkg = app.package(package)

    if pkg:
        log.header("Package detail for " + package).line()
        dump(pkg)
        print()
        log.header2("Deep merged configs")
        dump(pkg.config())
    else:
        typer.echo(f"Package {package} not found")

@providers.command()
def providers_cmd(json: bool = False):
    """Show providers graph"""
    if json:
        print(JSON.dumps(app.providers))
    else:
        log.header("Package provider graph (in exact order of registration dependency)").line()
        for (name, detail) in app.providers.items():
            log.info(name)
            dump(detail)
            print()
