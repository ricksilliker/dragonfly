import buffer


BUFFERVIEW_TARGET_ARRAY_BUFFER = 34962
BUFFERVIEW_TARGET_ELEMENT_ARRAY_BUFFER = 34963


class BufferView(object):
    def __init__(self):
        # int >= 0
        self.buffer = 0  # required
        # int >= 0
        self.byteOffset = 0
        # int >= 1
        self.byteLength = None  # required
        # int min >= 4, max <= 252
        self.byteStride = None
        # int, must be one of the BUFFER_TARGET_* constants
        self.target = None
        # str
        self.name = None
        # dict
        self.extensions = None
        # any
        self.extras = None

    @staticmethod
    def addBufferView(buffer, binaryData):
        if not isinstance(buffer, buffer.Buffer):
            raise TypeError('buffer must be of type {0}'.format(buffer.Buffer))

        if not isinstance(buffer, buffer.Buffer):
            raise TypeError('buffer must be of type {0}'.format(buffer.Buffer))

        buffView = BufferView()

        byteOffset = len(buffer.data)
        buffView.byteOffset = offset

        buffer.data += binaryData

        padding = (4 - (len(binaryData) % 4)) % 4
        buffer.data += b'\x00' * padding

        buffView.buffer = buffer.index
        buffView.byteLength = len(binaryData)

        return buffView

