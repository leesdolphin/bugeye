__author__ = 'lee'

import asyncio
import os
import re
import json
from .time import midnight_time

_loadedStores = {}
_folder = './store'

"""
Replace spaces with - and then remove any non-path characters.
"""
def pathify(name):

    return re.sub(r'[^0-9a-zA-Z\-_]', '', re.sub('\s+', '-', name))

class Mixer(object):

    def __init__(self, room, data_dir, on_media, on_feed):
        """
        Create a mixer.  Parameters:

        :param room:
                    For live editing this is the room name.  For post editing
                    this is None.

        :param data_dir:
                    The mixer will save the media feeds under this directory,
                    and read it's input feeds from this directory in "post"
                    mode.

        :param on_media:
                    A function called to give raw WebM data to the server.
                    Each call may come from a different thread.  Do not block
                    the thread by doing I/O.  It takes three parameters:

                     on_media(feed_idx, settings_id, data)

                    Feed_idx is an index into the feeds returned by
                    get_feeds(), settings_id is the settings_id parameter to
                    set_media(), and data is the raw WebB frame(s).  Calls
                    to this function cease when on_feed fires, and are
                    resumed when set_media() is called for the feed.

        :param on_feed function:
                    A function called when the feeds returned by get_feeds()
                    may have changed.  Each call may come from a different
                    thread.  Do not block the thread by doing I/O.  It takes
                    no arguments.  In "live" mode this only happens as part
                    of a set_feeds() call, in "post" mode it can happen
                    at any time.
        """
        self.room = room
        pass

    def set_feeds(self, feeds):
        """
        Set the input feeds for "live" mode.  Not used for "post" mode.
        Feeds is a sequence:

          [None, ("url", "type", "desc"), ...]

        The feeds are the same sequence as the "media" array returned by
        /config.  "url" is the URL the feed can be collected from using
        a HTTP request, something like "http://ip:port" or maybe
        "rtp://ip:port".  "type" is one of "audio", "video" or "av".
        "desc" is the descrption.
        """
        pass

    def get_feeds(self):
        """
        Return the current feeds.  Format same as "set_feeds()".

        """
        pass

    def set_mix(self, settings):
        """
        Set the mixing instructions.  Settings is a dict, all keys are
        optional.

           {
              'audio': n,
              'pip': n,
              'video': n,
           }

        Here n specified the input media stream.  It is the index into
        the feeds as returned by get_feeds().

        :param settings:
        :return:
        """
        pass


    def set_media(self, setting_id, feed_idx, scale, quality, fps):
        """
        Set the media format for an output stream (ie, as passed to
        on_media).  It also starts the data flowing to on_media for a feed.

        Params:

        :param setting_id
                    Anything.  It is only use is as a paramater to
                    on_media.

        :param feed_idx
                    Index into the feeds returned by get_feeds().  Index
                    0 is the mixed output feed.

        :param scale
                    Downscale by this factor, a float 0.0 ... 1.0.

        :param quality
                    jpeg quality, a number from 0 ... 100, or -1 for
                    same as input.

        :param fps
                    Output frames per second.
        """
        pass
