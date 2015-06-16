import asyncio

__author__ = 'lee'

API_VERSION = "v1"




@asyncio.coroutine
def init_api(loop, app, mixer):
    import bugeye.v1.live as live_api
    # import .post as post_api
    yield from live_api.init_api(loop, app, mixer)
