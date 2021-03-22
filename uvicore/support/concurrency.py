import uvicore
import asyncio
import functools
from uvicore.typing import Callable, TypeVar, Any
from uvicore.support.dumper import dump, dd

try:
    import contextvars  # Python 3.7+ only.
except ImportError:  # pragma: no cover
    contextvars = None  # type: ignore

T = TypeVar("T")

async def run_in_threadpool(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    loop = asyncio.get_event_loop()
    if contextvars is not None:  # pragma: no cover
        # Ensure we run in the same context
        child = functools.partial(func, *args, **kwargs)
        context = contextvars.copy_context()
        func = context.run
        args = (child,)
    elif kwargs:  # pragma: no cover
        # loop.run_in_executor doesn't accept 'kwargs', so bind them in here
        func = functools.partial(func, **kwargs)
    return await loop.run_in_executor(None, func, *args)



# Does not work as I need it to
# from asgiref.sync import async_to_sync
# def asyncmethodOBSOLETE_TEST(func):
#     """Convert an async method into a sync method if running synchronously"""
#     def decorator(*args, **kwargs):
#         do_async = False

#         if do_async == False:
#         #if not uvicore.app.is_async:
#             # If NOT running async (so from CLI) convert all async calls to sync
#             value = async_to_sync(func)(*args, **kwargs)



#             # if async_to_sync.launch_map:
#             #     # Event loop already exists, call function asynchronously
#             #     dump(async_to_sync.__dict__)
#             #     value = func(*args, **kwargs)
#             # else:
#             #     # No event loop started, create a new one
#             #     value = async_to_sync(func)(*args, **kwargs)

#             # try:
#             #     #dump(async_to_sync.__dict__)
#             #     value = async_to_sync(func)(*args, **kwargs)
#             # except RuntimeError:
#             #     # Exception means event loop is already running
#             #     # So don't async_to_sync again or you get RuntimeError
#             #     # "You cannot use AsyncToSync in the same thread as an async event loop - "
#             #     # "just await the async function directly."
#             #     value = func(*args, **kwargs)
#         else:
#             # If running async, call async func normally
#             value = func(*args, **kwargs)
#         return value
#     return decorator
