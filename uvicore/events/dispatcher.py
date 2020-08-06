import re
import uvicore
import inspect
from typing import Dict, List, Any, Union
from uvicore.support.dumper import dump, dd
from types import SimpleNamespace as obj
from collections import namedtuple
from uvicore.contracts import Dispatcher as DispatcherInterface
from uvicore.support import module


class _Dispatcher(DispatcherInterface):

    @property
    def events(self) -> Dict:
        return self._events

    @property
    def listeners(self) -> Dict[str, List]:
        return self._listeners

    @property
    def wildcards(self) -> List:
        return self._wildcards

    def __init__(self) -> None:
        self._events = {}
        self._listeners = {}
        self._wildcards = []

    def register(self, events: Dict):
        # Merge (but not deep) with existing events
        # Merging allows override by other later defined packages
        self._events = {**self.events, **events}
        pass

    def listen(self, events: Union[str, List], listener: Any) -> None:
        if type(events) == str: events = [events]

        # Do NOT check self.events for listener verification becuase self.events
        # is probably empty at this stage.  All registrations and listeners are
        # applied in service provider register() methods so cannot rely on
        # self.events being full and complete.  This means we cannot propert
        # match wildcard events to actual events.

        # Expand all wildcards
        for event in events:
            if event not in self.listeners:
                self._listeners[event] = []
            self._listeners[event].append(listener)
            if '*' in event:
                self._wildcards.append(event)

    def subscribe(self, listener: str) -> None:
        try:
            module.load(listener).object().subscribe(uvicore.events)
        except ModuleNotFoundError:
            pass

    def dispatch(self, event: Any, payload = {}) -> None:
        # When using this actual uvicore.events.dispatch(MyEvent())
        # In other words, passing in a class instance, we want to call
        # the class .dispatch() method itself instead if just passing it
        # on to _dispatch below.  Why?  Because users will override the
        # dispatch method and we always want to make sure that runs.
        # If users call MyEvent().dispatch() this method is never hit
        # and _dispatch is called directly.

        # Get event by string name or class inspection
        event_meta = self.get_event(event)

        # Event not registered, dispatch nothing
        if not event_meta: return

        if type(event) == str:
            try:
                # See if string event has a matching class.  If so, import and dispatch it
                module.load(event).object(**payload).dispatch()
            except ModuleNotFoundError:
                # No class found for this string.  This is OK because events can
                # be strings without matching classes.  Dispatch it anyway
                self._dispatch(event, payload)
        else:
            # Event is a class.  Call the actual classes dispatch method
            # in case the user overrode it, we still execute it
            event.dispatch()

    def _dispatch(self, event: Any, payload = {}) -> None:
        # Get event by string name or class inspection
        event_meta = self.get_event(event)

        # Event not registered, dispatch nothing
        if not event_meta: return

        if type(event) == str:
            # Event is a string.  Convert payload into an object
            # so the data is accessible as if it were a class based event
            #payload['event'] = event_meta
            if payload:
                payload = namedtuple('payload', sorted(payload))(**payload)
            else:
                payload = None
        else:
            # Event is a class or method.  The payload is the instantiated
            # class itself and the event is the classes MODULE name, not the class name itself
            payload = event
            event = str(event.__class__).split("'")[1]
            #event_meta = self.events.get(event)
            #event_meta['name'] = event
            #setattr(payload, 'event', event_meta)

        # Fire all event listeners
        self._fire_listeners(event_meta, payload)

    def _fire_listeners(self, event: Dict, payload: Dict) -> None:
        listeners = self.get_listeners(event['name'])
        for listener in listeners:
            # New up the listener
            if type(listener) == str:
                try:
                    module.load(listener).object(uvicore.app).handle(event, payload)
                except ModuleNotFoundError:
                    # Bad listener, skip
                    pass
            else:
                listener(event, payload)

    def get_listeners(self, event: str) -> List:
        listeners = []
        if event in self.listeners:
            listeners += self.listeners[event]

        for wildcard in self.wildcards:
            if re.search(wildcard, event):
            # if wildcard.replace('*', '') in event:
                listeners += self.listeners[wildcard]

        return listeners

    def get_event(self, event: Any) -> Dict:
        if type(event) == str:
            name = event
        else:
            name = str(event.__class__).split("'")[1]
        if name in self.events:
            event_meta = self.events.get(name)
            event_meta['name'] = name
            return event_meta
