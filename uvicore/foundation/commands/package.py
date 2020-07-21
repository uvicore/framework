import typer
from uvicore import app
from uvicore.support.dumper import dd, dump


list = typer.Typer()
@list.command()
def list_cmd():
    """List all packages"""
    for package in app.packages:
        dump(package)
        #dump(f"== {package.name} deep merged configs --")
        #dump(package.config())


show = typer.Typer()
@show.command()
def show_cmd(package: str):
    """Show detailed info for one package"""
    if package == 'main':
        pkg = app.package(main=True)
    else:
        pkg = app.package(package)
    dump(pkg)
    typer.secho(f"::- {package} deep merged configs -::", fg=typer.colors.GREEN)
    dump(pkg.config())


