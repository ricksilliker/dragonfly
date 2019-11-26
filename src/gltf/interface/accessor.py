COMPONENT_TYPE_BYTE = 5120
COMPONENT_TYPE_UNSIGNED_BYTE = 5121
COMPONENT_TYPE_SHORT = 5122
COMPONENT_TYPE_UNSIGNED_SHORT = 5123
COMPONENT_TYPE_UNSIGNED_INT = 5125
COMPONENT_TYPE_FLOAT = 5126


DATA_TYPE_SCALAR = "SCALAR"
DATA_TYPE_VEC2 = "VEC2"
DATA_TYPE_VEC3 = "VEC3"
DATA_TYPE_VEC4 = "VEC4"
DATA_TYPE_MAT2 = "MAT2"
DATA_TYPE_MAT3 = "MAT3"
DATA_TYPE_MAT4 = "MAT4"


class Accessor(object):
    def __init__(self):
        # int, >= 0
        self.bufferView = None
        # int, >= 0
        self.byteOffset = 0
        # int, must be one of the 6 COMPONENT_TYPE_* constants
        self.componentType = None  # required
        # bool
        self.normalized = False  # required
        # int, >= 1
        self.count = None  # required
        # str, must be one of the 7 DATA_TYPE_* constants
        self.type = None  # required
        # float, based on the component type, can be 1, 2, 3, 4, 9, or 16
        self.max = None
        # float, based on the component type, can be 1, 2, 3, 4, 9, or 16
        self.min = None
        # dict
        self.sparse = None
        # str
        self.name = None
        # dict
        self.extensions = None
        # any
        self.extras = None

        