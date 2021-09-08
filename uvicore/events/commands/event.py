import uvicore
from uvicore import log
from uvicore.support.dumper import dd, dump
from uvicore.console import command, argument

# Commands
#list = typer.Typer()
#show = typer.Typer()


@command()
def list():
    """List all events"""
    log.header("Events defined from all packages")
    log.line()

    event_bindings = uvicore.ioc.binding(type='event')
    events = []
    for binding in event_bindings.values():
        events.append({
            'name': binding.path,
            'description': binding.object.__doc__,
            'is_async': binding.object.is_async,
        })
    dump(events)


@command()
@argument('event')
def get(event: str):
    """Show detailed info for one event"""
    log.header("Event details for " + event)
    log.line()

    event_bindings = uvicore.ioc.binding(type='event')
    events = []
    for binding in event_bindings.values():
        if event == binding.path:
            events.append({
                'name': binding.path,
                'description': binding.object.__doc__,
                'is_async': binding.object.is_async,
            })
    if events:
        dump(events)
    else:
        print("Event {} not found".format(event))


@command()
def listeners():
    """Show all event listeners/handlers"""
    log.header("Event listeners/handlers")
    log.line()

    #dump(uvicore.events.expanded_sorted_listeners)
    dump(uvicore.events.listeners)
