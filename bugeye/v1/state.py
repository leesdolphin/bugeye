import asyncio
from bugeye.store import Mixer
from collections import namedtuple

def run_soon(loop, coroutine, *args):
    def do_run():
        loop.create_task(coroutine(*args))
    loop.call_soon_threadsafe(do_run)

class MixerWrapper(object):

    SUPPORTED_STATES = frozenset(['audio', 'video', 'pip'])
    MEDIA_TUPLE = namedtuple("MediaTuple", ["feed_idx", "setting_id"])

    def __init__(self, loop, room, data_dir):
        self._loop = loop
        self._mixer = Mixer(room, data_dir, self._on_media, self._on_feed)
        self._state = {}
        self.responses = {}

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        state = {}
        for s in self.SUPPORTED_STATES:
            ## Get or default. This also does an implicit copy
            state[s] = int(new_state.get(s, 0))
        self._state = state
        self._mixer.set_mix(self._state)

    @property
    def feeds(self):
        return self._mixer.get_feeds()

    @feeds.setter
    def feeds(self, feeds):
        self._mixer.set_feeds(feeds)

    def _on_feed(self):
        ## !!CALLED FROM THREAD!!

        ## Run close_all on the event loop.
        ## Even if this function is called on another thread.
        run_soon(self._loop, self.close_all)

    @asyncio.coroutine
    def close_all(self):
        for response in self.responses.values():
            ## TODO: Pop from open_response dict
            yield from response.write_eof()

    def _on_media(self, feed_idx, settings_id, data):
        ## !!CALLED FROM THREAD!!
        media_id = self.MEDIA_TUPLE(feed_idx, settings_id)
        run_soon(self._loop, self.write_media, media_id, data)

    @asyncio.coroutine
    def _write_media(self, media_id, data):
        if media_id in self.responses:
            resp = self.responses[media_id]
            try:
                resp.write(data)
            except:
                ## Probably a write error - remove this id and then pass the
                ## error up the chain
                if id in self.responses:
                    del self.responses[media_id]
                raise

    def add_media(self, ):














