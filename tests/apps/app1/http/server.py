from app1.package import bootstrap

# Bootstrap the Uvicore application
#app = bootstrap.application(is_console=False)
app = bootstrap.Application(is_console=False)()

# Http entrypoint for uvicorn or gunicorn
# uvicorn --port 5000 mreschke.wiki.http.server:http --reload
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:5000 mreschke.wiki.http.server:http
http = app.http



# loop = None
# def http(scope):
#     #https://github.com/encode/uvicorn/issues/706
#     global loop

#     if scope['type'] == 'lifespan':
#         print('lifespan')
#         loop = asyncio.get_running_loop()
#         loop.create_task(bootstrap.application(is_console=False))
#         #loop.run_until_complete(bootstrap.application(is_console=False))
#         print('xxxxxxxx')

#     if scope['type'] == 'http':
#         print('req')
#         async def asgi(receive, send):

#             scope['app'] = uvicore.app.http
#             await uvicore.app.http.middleware_stack(scope, receive, send)
#         return asgi


# def http(scope):
#     assert scope["type"] == "http"  # Ignore anything other than HTTP

#     async def asgi(receive, send):
#         await send({
#             "type": "http.response.start",
#             "status": 200,
#             "headers": [
#                 [b"content-type", b"text/plain"],
#             ],
#         })
#         await send({
#             "type": "http.response.body",
#             "body": b"Hello, World!",
#         })

#     return asgi
