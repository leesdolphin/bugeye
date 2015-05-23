__author__ = 'lee'

import asyncio
from aiohttp import web

import bugeye.middlewares as middlewares

class ServeStaticRoute(web.StaticRoute):
    ## TODO: Handle loading files from inside packaged file.
    ## TODO: Handle providing index.html at /
    pass


class APIHandler(web.UrlDispatcher)


@asyncio.coroutine
def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(body=text.encode('utf-8'))


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop, middlewares=(middlewares.pretty_error,))
    assert isinstance(app.router, web.UrlDispatcher)
    app.router.register_route(ServeStaticRoute("static", "static/", "static/"))
    app.router.add_route('GET', '/{name}', handle)
    app.router.add_static('static/', 'static/', )
    srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 8080)
    print("Server started at http://127.0.0.1:8080")
    return srv


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

# from tornado.ioloop import IOLoop
# from tornado.web import RequestHandler, Application, url
#
#
# class UIHandler(RequestHandler):
#     def get(self):
#         self.render("index.html")
#
#
# class VideoHandler(RequestHandler):
#     def get(self):
#         with open('video.mp4', 'rb') as vid:
#         #with open('video.mkv', 'rb') as vid:
#             self.set_header('Content-Type', 'video/mp4')
#             self.write(vid.read())
#             #count = 1
#             #while True:
#                 #chunk = vid.read(8*1024*10)
#                 #if not chunk:
#                     #break
#                 #print('chunk %d written' % count)
#                 #count += 1
#                 #self.write(chunk)
#                 #self.flush()
#             self.finish()
#
#
# def make_app():
#     return Application([
#         url(r"/", UIHandler),
#         url(r"/video.mkv", VideoHandler),
#     ], static_path='static')
#
#
# def main():
#     app = make_app()
#     app.listen(8000)
#     IOLoop.current().start()
#

