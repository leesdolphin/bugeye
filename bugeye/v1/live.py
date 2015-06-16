from . import API_VERSION
import asyncio
import json
import functools
from aiohttp import web
import aiohttp

dump_json = functools.partial(json.dumps, indent=4, sort_keys=True)


class JsonResponse(web.Response):

    def __init__(self, object):
        super().__init__(content_type='application/json')
        self.text = dump_json(object)


class BaseEndpoint(object):

    def __init__(self, loop, app, mixer):
        self.loop = loop
        self._mixer = mixer
        self._app = app

    def __add_route(self, method, path, handler,
                   *_, **kwargs):
        path = '/' + API_VERSION + path
        if 'name' in kwargs:
            kwargs['name'] = kwargs['name'] + '-' + API_VERSION
        print(method, path, handler, kwargs)
        self._app.router.add_route(method, path, handler, **kwargs)

    def _add_methods(self, method_handlers):
        base_path = self.PATH.lstrip('/')
        for method, handler in method_handlers.items():
            name = method + "-" + base_path
            self.__add_route(method, "/" + base_path, handler, name=name)

    @property
    def path(self):
        return "/" + API_VERSION + self.PATH


class NotifyEndpointMixin(BaseEndpoint):

    def __init__(self, loop, app, mixer):
        super().__init__(loop, app, mixer)
        self._notifier = None

    @property
    def notifier(self):
        if self._notifier:
            return self._notifier
        else:
            raise Exception("Notifier not set.")

    @notifier.setter
    def notifier(self, new_notifier):
        self._notifier = new_notifier

    def notify_update(self, uri=None):
        if not uri:
            uri = self.path
        self._loop.call_soon_threadsafe(self.notifier.notify, uri)


class ConfigEndpoints(BaseEndpoint):

    PATH = '/config'

    def init_routes(self):
        self._add_methods({
            'GET': self.get,
         })

    @asyncio.coroutine
    def get(self, request):
        feeds = self._mixer.get_feeds()
        output = []
        for feed in feeds:
            feed_out = {}
            if feed:
                feed_out['href'] = feed[0]
                feed_out['type'] = feed[1]
                feed_out['name'] = feed[2]
            output.append(feed_out)
        return JsonResponse(output)

class NotifierEndpoint(BaseEndpoint):

    PATH = '/notify'

    def __init__(self, loop, app, mixer):
        super().__init__(loop, app, mixer)
        self._clients = []

    def init_routes(self):
        self._add_methods({
            'GET': self.connect
        })

    @asyncio.coroutine
    def connect(self, request):
        ws = web.WebSocketResponse()
        ws.start(request)
        self._add_ws(ws)

        while True:
            if ws.closed:
                return (yield from self._del_ws(ws))
            msg = yield from ws.receive()
            if msg.tp == aiohttp.MsgType.close:
                print('websocket connection closed')
                return (yield from self._del_ws(ws))
            elif msg.tp == aiohttp.MsgType.error:
                print('ws connection closed with exception %s',
                      ws.exception())
                return (yield from self._del_ws(ws))

        return ws

    def _add_ws(self, ws):
        self._clients.append(ws)

    @asyncio.coroutine
    def _del_ws(self, ws):
        if not ws.closed:
            yield from ws.close()
        try:
            self._clients.remove(ws)
        except ValueError as e:
            pass ## Websocket already gone.
        return ws

    @asyncio.coroutine
    def notify(self, uri):
        for client in self._clients:
            if not client.closed:
                client.send_str(uri)


class MixEndpoint(NotifyEndpointMixin):

    PATH = '/mix'
    _mixer_state = {'main': 1, 'audio': 2, 'pip': 0}

    def init_routes(self):
        self._add_methods({
            'GET': self.get,
            'POST': self.post,
         })

    @asyncio.coroutine
    def get(self, request):
        return JsonResponse(self._mixer_state)

    @asyncio.coroutine
    def post(self, request):
        self.notify_update()


@asyncio.coroutine
def init_api(loop, app, mixer):
    args = [loop, app, mixer]
    notify = NotifierEndpoint(*args)
    cfg = ConfigEndpoints(*args)
    mix = MixEndpoint(*args)
    for endpoint in [notify, cfg, mix]:
        endpoint.init_routes()
    for endpoint in [mix]:
        endpoint.notifier = notify