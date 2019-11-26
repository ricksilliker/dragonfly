PRIMITIVE_TYPE_POINTS = 0
PRIMITIVE_TYPE_LINES = 1
PRIMITIVE_TYPE_LINE_LOOP = 2
PRIMITIVE_TYPE_LINE_STRIP = 3
PRIMITIVE_TYPE_TRIANGLES = 4
PRIMITIVE_TYPE_TRIANGLE_STRIP = 5
PRIMITIVE_TYPE_TRIANGLE_FAN = 6

class Mesh(object):
    def __init__(self):
        # Union[list, Primitive]
        self.primitives = None  # required
        # Union[list, int]
        self.weights = None
        # str
        self.name = None
        # dict
        self.extensions = None
        # any
        self.extras = None

class Primitive(object):
    def __init__(self):
        # dict, typically stores the POSITION and NORMAL key accessor indices
        self.attributes = None  # required
        # int, >= 0
        self.indices = None
        # int, >= 0
        self.material = None
        # int, must be one of the PRIMITIVE_TYPE_* constants
        self.mode = 4
        # Union[list, dict]
        self.targets = None
        # dict
        self.extensions = None
        # any
        self.extras = None
