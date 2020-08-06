# Events


## Introduction

Uvicore provides an observer (pub/sub) implementation allowing you to listen
(subscribe) to events that occure in the framework and in your own packages.

Events are a great way to decouple various aspects of your project.  A single
event can have many listeners that need not depend on each other.  For example,
each time a wiki post is created you may wish to send an email or slack
notification to all watchers of the post.

All events must be pre-registered with uvicore.  This allows the framework to
know all possible events for all packages.  Running `./uvicore events list` will
show you this events database.

Events are dispatched throughout the framework and other packages.  When an
event is dispatched all defined listeners will be called in order they were
added.  Listeners define the event(s) to watch and the event handlers (callbacks)
to fire when then event is dispatched.  Handlers can be methods, classes or
even bulk listening/handling subscriptions.


## Defining Your Own Events

The first step in creating your own events is to pick an event name, then
register that event with the framework.  The best place to register your own
events is in your package Service Provider `register()` method.

**Register Events**

```python
# services/wiki.py
from uvicore.support.provider import ServiceProvider

class Wiki(ServiceProvider):

    def register(self):

        # Register events used in this package
        self.events({
            'mreschke.wiki.events.post.Created': {
                'description': 'Wiki post has been created',
                'type': 'class',
                # ...
                # There is no set definition of what should be here.  This is
                # your own metadata for an event.  Could define log output
                # text, log icons or sections, priority, severity or anything
                # you want.  This metadata is passed along to each handler.
            },
            'mreschke.wiki.events.post.Deleted': {
                'description': 'Wiki post has been deleted',
                'type': 'class',
            },
        })
    # ...
```

The second step is OPTIONAL.  You must decide if you want to create a matching
event class that acts as a payload container and parameter contract.  Or simply
treat the event as a string based event with Dictionary payload parameters.

The benifits of an event class are that you can force the payload requirements
using the class `__init__()` constructor.  An event class performs NO work.  It
is simply a data container for the payload itself.  Event classes are typically
stored in the `events` directory of your package.  If using a simple string to
define an event, it is best practice to name the string as if it were going to
be an actual event class someday.  For example
`mreschke.wiki.events.post.Created`. If at some point you want to create the
actual class, all existing listeners that use that string will not need to be
changed as the system looks for a class of the same name to instantiate.

**Event Payload Class**

```python
# events/post.py
from uvicore.events import Event
from mreschke.wiki.models import Post

class Created(Event):

    def __init__(self, post: Post):
        self.post = post
```

That's it.  Seems simple.  An event class contains no logic.  It is simply a
container with a constructor that forces a specific payload.  This helps
constrain the dispatch code and also provides Code IDE intellisense when newing
up the event to dispatch.  This class is completely optional.  The event can
still be dispatched without it.




## Dispatching Events

You can fire off (dispatch) a registered event in a few different ways.  Where
you fire off the event is up to your own code.  With the Wiki events
example above the proper place may be in your controller, model or job that
Creates and Deletes wiki posts.  Wherever the location, fireing off an event
is simple.

**As a String**

The framework will use this string to check if a matching event class exists.
If the class exists it will import it and new it up using the dictionary as
the `__init__()` constructor parameters.  If the class does not exist, this
event will still fire as usual using the dictionary as an unconstrained payload.
```python
from uvicore import events
events.dispatch('mreschke.wiki.events.post.Created', {'post': post})
```

**As a Class Instance**

You can new up the event class yourself.  The benefits of this over the string
approach is IDE auto-completion.  Your IDE will show you the exact parameters
required to new up the class.  The payload is now constrained to a contract.

When newing up the event class yourself you have two options of how to dispatch it.
```python
from uvicore import events
from mreschke.wiki.events import Created

# Using the events.dispatch() method to pass in the class instance
events.dispatch(Created(post))

# Or by using the event classes build-in .dispatch() method
Created(post).dispatch()
```

However you dispatch your events, all listeners are immediately fired in order
they were defined.




## Listening to Events

Registering and then dispatching events do nothing if there is no one listening.
Listeners define callbacks that are executed when an event is dispatched.

The best place to register your event listeners is in your package Service
Provider `register()` method which has access to `self.listen` and
`self.subscribe` event helper methods.


**Listen to a single event**

```python
# From service provider register() method

# Use a local method (function) as the callback
self.listen('mreschke.wiki.post.Created', self.NotifyUsers)

# Use a listener class as the callback
self.listen('mreschke.wiki.post.Created', 'mreschke.wiki.listeners.NotifyUsers')
```

!!! info
    Notice the `mreschke.wiki.listeners.NotifyUsers` class is defined as a
    string in dot notation.  The event system will automatically instantiate
    and call the class `handle()` method during dispatch.


**Listen to multiple events**

```python
# From service provider register() method

# Use a local method (function) as the callback
self.listen([
    'mreschke.wiki.post.Created',
    'mreschke.wiki.post.Deleted',
], self.NotifyUsers)

# Use a listener class as the callback
self.listen([
    'mreschke.wiki.post.Created',
    'mreschke.wiki.post.Deleted',
], 'mreschke.wiki.listeners.NotifyUsers')
```

**Listen to wildcard events**

```python
# From service provider register() method

# Use a local method (function) as the callback
self.listen('uvicore.foundation.events.*', self.NotifyUsers)

# Use a listener class as the callback
self.listen('uvicore.foundation.events.*', 'mreschke.wiki.listeners.NotifyUsers')

# The * wildcard also works in the middle of an event name
self.listen('mreschke.wiki.models.*.Deleted', self.LogDeletions)
```

**Registering a subscriber**

A subscription is an all-in-one class which listens to one or more events and
also contains the handlers for each event.  Notice we are not defining the
event to listen to here.  We simply define the subscription class.  See
[Handling Events](#handling-events) for what these classes look like.
```python
# From service provider register() method
self.subscribe('mreschke.wiki.listeners.HttpEventSubscription')
```




### Listeners outside a Service Provider

You can also listen and subscribe to events outside of a service provider by
using the `uvicore.events` instance.

```python
from uvicore import events
events.listen('mreschke.wiki.post.Created', self.my_handler)
events.subscribe('mreschke.wiki.listeners.HttpEventSubscription')
```




## Handling Events

Handlers are callbacks that are dispatched when an event fires.  Handlers are
defined using `listen()` or `subscribe()` methods as noted in
[Listening To Events](#listening-to-events).

Handlers can be basic python methods (functions) or dedicated handler classes.

All handlers receive an `event: Dict` and `payload: Any`.  The `event`
dictionary is the metadata for an event that was defined by the developer
during the event registration.  If the event listener is a class, the payload
will be an instance of that class with properties of all constructor parameters.
If the event listener is just a string, the payload is a `namedtuple` of
parameters.

**Method Handler**

```python
def my_handler(event: Dict, payload: Any) -> None:
    # Do work when this event is dispatched.
```

**Class Handler**

```python
from typing import Dict, Any
from uvicore.events.handler import Handler

class NotifyUser(Handler):

    def handle(self, event: Dict, payload: Any):
        # Instance variable self.app is also available to you
        # Do work when this event is dispatched.
```

**Subscription Handlers**

Subscriptions are a great way to listen and handle multiple events from a single
file.

```python
from typing import Dict, Any
from uvicore.contracts import Dispatcher

class AppEventSubscription:

    def app_registered(self, event: Dict, payload: Any):
        #  Do something when then the framework is done registering all providers

    def app_booted(self, event: Dict, payload: Any):
        #  Do something when then the framework is done booting all providers

    def post_created(self, event: Dict, payload: Any):
        #  Do something when a wiki post is created

    def subscribe(self, events: Dispatcher):
        # A subscription is an all in one class that can both listen AND handle
        # one or more events in a single place.
        events.listen('uvicore.foundation.events.app.Registered', self.app_registered)
        events.listen('uvicore.foundation.events.app.Booted', self.app_booted)
        events.listen('mreschke.wiki.post.Created', self.post_created)
```
