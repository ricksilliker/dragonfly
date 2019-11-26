class Buffer(object):
    def __init__(self):
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