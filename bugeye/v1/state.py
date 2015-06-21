

class MixerWrapper(object):

    SUPPORTED_STATES = frozenset(['audio', 'video', 'pip'])

    def __init__(self, loop, mixer):
        self._loop = loop
        self._mixer = mixer
        self._state = {}

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

    




