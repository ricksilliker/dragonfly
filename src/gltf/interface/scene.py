class Scene(object):
    def __init__(self):
        # Union[list, int], >= 0 per item
        self.nodes = None
        # str
        self.name = None
        # dict
        self.extensions = None
        # any
        self.extras = None