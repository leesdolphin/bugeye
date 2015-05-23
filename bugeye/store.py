__author__ = 'lee'

import asyncio
import os
import re
import json

_loadedStores = {}
_folder = './store'

def pathify(name):
    return re.sub(r'[^0-9a-zA-Z\-_]', '', re.sub('\s+', '-', name))



def set_folder(folder):
    _folder = folder

class Room(object):

    def __int__(self, name):
        self.__name = name
        self.load_json()

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    def serialise_state(self, is_internal=True):
        state = {}
        state['room'] = self.name;
        if not is_internal:
            state['media'] = self.serialise_media()
            state['time'] = ticker.midnight_time()
        else:
            






@asyncio.coroutine
def get_room(room_name):
    if room_name not in _loadedStores:
        _loadedStores[room_name] = yield from load_room(room_name)
    return _loadedStores[room_name]

@asyncio.coroutine
def load_room(room_name):
    return Room(room_name)

