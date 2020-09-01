import uvicore
from asgiref.sync import async_to_sync
from uvicore.support.dumper import dump, dd

def asyncmethod(method):
    """Convert an async method into a sync method if running synchronously"""
    def decorator(*args, **kwargs):
        if not uvicore.app.is_async:
            # If NOT running async (so from CLI) convert all async calls to sync
            value = async_to_sync(method)(*args, **kwargs)



            # if async_to_sync.launch_map:
            #     # Event loop already exists, call function asynchronously
            #     dump(async_to_sync.__dict__)
            #     value = method(*args, **kwargs)
            # else:
            #     # No event loop started, create a new one
            #     value = async_to_sync(method)(*args, **kwargs)

            # try:
            #     #dump(async_to_sync.__dict__)
            #     value = async_to_sync(method)(*args, **kwargs)
            # except RuntimeError:
            #     # Exception means event loop is already running
            #     # So don't async_to_sync again or you get RuntimeError
            #     # "You cannot use AsyncToSync in the same thread as an async event loop - "
            #     # "just await the async function directly."
            #     value = method(*args, **kwargs)
        else:
            # If running async, call async method normally
            value = method(*args, **kwargs)
        return value
    return decorator
