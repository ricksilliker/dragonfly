IDENTITY_MATRIX = [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]

class Node(object):
    def __init__(self):
        # int >= 0
        self.camera = None
        # Union[list, int], >= 0 per item
        self.children
        # int >= 0
        self.skin
        # Union[list, float][16]
        self.matrix = IDENTITY_MATRIX
        # int, >= 0
        self.mesh = None
        # Union[list, float][4]
        self.rotation = [0,0,0,1]
        # Union[list, float][3]
        self.scale = [1,1,1]
        # Union[list, float][3]
        self.translation = [0,0,0]
        # Union[list, int]
        self.weights = None
        # str
        self.name = None
        # dict
        self.extensions = None
        # any
        self.extras = None
