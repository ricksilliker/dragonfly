import base64
import logging

class Buffer(object):
    def __init__(self, bufferIndex=0):
        # str
        self.uri = None
        # int >= 1
        self.byteLength = 1  # required.
        # str
        self.name = None
        # dict
        self.extensions = None
        # any
        self.extras = None

        self._data = b''
        self._bufferIndex = bufferIndex

    def getByteLength(self):
        return len(self._data)

    @property
    def data(self):
        return self._data

    @property
    def index(self):
        return self._bufferIndex





    