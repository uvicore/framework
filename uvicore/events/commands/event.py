import typer
import uvicore
from uvicore import log
from uvicore.support.dumper import dd, dump

# Commands
list = typer.Typer()
show = typer.Typer()


@list.command()
def list_cmd():
    """List all events"""
    log.header("Events defined from all packages").line()
    dump(uvicore.events.events)


@show.command()
def show_cmd(event: str):
    """Show detailed info for one event"""
    log.header("Event details for " + event).line()
    event = uvicore.events.get_event(event)
    if event:
        dump(event)
    else:
        typer.echo(f"Event {event} not found")
