__author__ = 'lee'

import asyncio
from aiohttp import web
import json
from bugeye.time import midnight_time
from bugeye.store import Mixer
import bugeye.middlewares as middlewares

class ServeStaticRoute(web.StaticRoute):
    ## TODO: Handle loading files from inside packaged file.
    ## TODO: Handle providing index.html at /
    pass


class LiveMixing(object):

    def __init__(self):
        self._rooms = {}
        pass

    def init_routes(self, app):
        app.router.add_route('GET', '/live/{room}/config', self.room_config_handler)

    @asyncio.coroutine
    def room_config_handler(self, request):
        response = web.Response()
        room_name = request.match_info["room"].lower()
        for room in rooms:
            if room.room.lower() == room_name:
                response.content_type = "text/json"
                response.body = self._room_to_json(room)
                return response
        # Reach here - no rooms
        response.set_status(404)
        return response

    def _room_to_json(self, room: bugeye.store.Mixer):
        """

        :param room:
        :type room: bugeye.store.Mixer
        :return: A JSON string.
        :rtype: basestring
        """
        config = {'room': room.room,
                  'media': room.get_feeds(),
                  'time': midnight_time()}
        return json.dumps(config, indent=2, sort_keys=True)



rooms = [Mixer("hi", None, None, None)]


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

