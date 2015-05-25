__author__ = 'lee'

import asyncio

asyncio._DEBUG = True
import os
from aiohttp import web
import json
from bugeye.time import midnight_time
from bugeye.store import Mixer
import bugeye.middlewares as middlewares

class ServeStaticRoute(web.StaticRoute):
    ## TODO: Handle loading files from inside packaged file.

    def match(self, path):
        if path in ['/', '/index.html']:
            return {'filename': 'index.html'}
        else:
            return super().match(path)

    def url(self, *, filename, query=None):
        while filename.startswith('/'):
            filename = filename[1:]
        if filename in ['/', '/index.html']:
            url = '/'
        else:
            url = self._prefix + filename
        return self._append_query(url, query)

    @asyncio.coroutine
    def handle(self, request):
        try:
            return (yield from super().handle(request))
        except web.HTTPNotFound as e:
            filename = request.match_info['filename']
            print("Accessing: ", filename, "; ", os.path.join(self._directory, filename))
            raise

class LiveMixing(object):

    def __init__(self):
        self._rooms = []
        pass

    def init_routes(self, app):
        app.router.add_route('GET', '/live/{room}/config', self.room_config_handler)
        app.router.add_route('GET', '/live/{room}/mix', self.change_mixer)

    @asyncio.coroutine
    def room_config_handler(self, request):
        response = web.Response()
        room = self.get_room(request.match_info["room"])
        if room is None:
            response.set_status(404)
        else:
            response.content_type = "application/json"

            config = {'room': room.room,
                      'media': room.get_feeds(),
                      'time': midnight_time()}
            response.text = json.dumps(config, indent=2, sort_keys=True)
            return response
        return response

    @asyncio.coroutine
    def change_mixer(self, request):
        response = web.Response()
        room = self.get_room(request.match_info["room"])
        if room is None:
            response.set_status(404)
        else:
            room.set_mix({
                "audio": request.GET.get("audio", 0),
                "video": request.GET.get("video", 0),
                "pip": request.GET.get("pip", 0),
            });
        return response

    @asyncio.coroutine
    def set_notes(self, request):
        response = web.Response()
        room = self.get_room(request.match_info["room"])
        if room is None:
            response.set_status(404)
        else:
            try:
                post_data = yield from response.post()
                talk_id = post_data['talk-id']
                talk_start = post_data['talk-begin']
                talk_end = post_data['talk-end']
                title = post_data['title']
                presenter = post_data['presenter']
                comments = post_data['comments']
            except KeyError as e:
                raise web.HTTPBadRequest() from e


        return response

    @staticmethod
    def get_room(self, name):
        print("Searching for", name)
        room_name = name.lower()
        for room in rooms:
            if room.room.lower() == room_name:
                return room
        return None


class Streaming(object):

    def __init__(self):
        pass

    def init_routes(self, app):
        app.router.add_route('GET', '/video.mkv', self.stream_test)
        pass

    @asyncio.coroutine
    def stream_test(self, request):
        print("Testing Stream: ", request)
        response = web.StreamResponse()
        chunk_size = 512
        import mimetypes
        content_type, encoding = mimetypes.guess_type("video.mp4")
        print("Testing Stream: ", request, " || ", content_type, encoding)
        response.enable_chunked_encoding()
        response.content_type = content_type
        response.start(request)
        yield from self.stream_file(open("bugeye/video.mp4", 'rb'), response, chunk_size)
        return response

    @asyncio.coroutine
    def stream_file(self, input_stream, started_response, chunk_size=512):
        def get_chunk():
            """

            :return: The next chunk of length `chunk_size`.
            """
            import time
            time.sleep(0.01)
            ## Caution: This function is run in a thread!
            return input_stream.read(chunk_size) or None
        print('Starting to stream file')
        yield from self.supply_chunks(get_chunk, started_response)
        print('Done streaming file')

    @staticmethod
    @asyncio.coroutine
    def supply_chunks(get_chunk_fn, output):
        """

        :param get_chunk_fn: A function taking no arguments and returning the next chunk(a type that can be
                             passed into `output.write()` or None(indicating EOF)
        :type get_chunk_fn: function()
        :param output: A output stream that will have chunks of data written to. This should be non-blocking
        :return: `False` if the end of the input stream indicated. `True` otherwise.
        """
        while True:
            chunk = yield from asyncio.get_event_loop().run_in_executor(None, get_chunk_fn)
            if chunk is not None:
                output.write(chunk)
            else:
                break;




rooms = [Mixer("hi", None, None, None)]


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop, middlewares=(middlewares.pretty_error,))
    assert isinstance(app.router, web.UrlDispatcher)
    app.router.register_route(ServeStaticRoute("Static Content", "/static/", "bugeye/static/"))
    live = LiveMixing()
    live.init_routes(app)

    streamer = Streaming()
    streamer.init_routes(app)

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

