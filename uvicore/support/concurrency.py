import uvicore
from uvicore.support.dumper import dump, dd
from starlette.concurrency import run_in_threadpool


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
