import typer
from uvicore import app
from uvicore.support.dumper import dd, dump

# Commands
list = typer.Typer()
show = typer.Typer()


@list.command()
def list_cmd():
    """List all packages"""
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
        dump(pkg)
        typer.secho(f"::- {package} deep merged configs -::", fg=typer.colors.GREEN)
        dump(pkg.config())
    else:
        typer.echo(f"Package {package} not found")


