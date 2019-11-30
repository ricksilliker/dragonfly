import json


COMPONENT_TYPE_BYTE = 5120
COMPONENT_TYPE_UNSIGNED_BYTE = 5121
COMPONENT_TYPE_SHORT = 5122
COMPONENT_TYPE_UNSIGNED_SHORT = 5123
COMPONENT_TYPE_UNSIGNED_INT = 5125
COMPONENT_TYPE_FLOAT = 5126

COMPONENT_TYPES = {
    'BYTE': COMPONENT_TYPE_BYTE,
    'UNSIGNED_BYTE': COMPONENT_TYPE_UNSIGNED_BYTE,
    'SHORT': COMPONENT_TYPE_SHORT,
    'UNSIGNED_SHORT': COMPONENT_TYPE_UNSIGNED_SHORT,
    'UNSIGNED_INT': COMPONENT_TYPE_UNSIGNED_INT,
    'FLOAT': COMPONENT_TYPE_FLOAT
}

COMPONENT_TYPE_CODES = {
    COMPONENT_TYPE_BYTE: 'b',
    COMPONENT_TYPE_UNSIGNED_BYTE: 'B',
    COMPONENT_TYPE_SHORT: 'h',
    COMPONENT_TYPE_UNSIGNED_SHORT: 'H',
    COMPONENT_TYPE_UNSIGNED_INT: 'I',
    COMPONENT_TYPE_FLOAT: 'f'
}

DATA_TYPE_SCALAR = "SCALAR"
DATA_TYPE_VEC2 = "VEC2"
DATA_TYPE_VEC3 = "VEC3"
DATA_TYPE_VEC4 = "VEC4"
DATA_TYPE_MAT2 = "MAT2"
DATA_TYPE_MAT3 = "MAT3"
DATA_TYPE_MAT4 = "MAT4"

IDENTITY_MATRIX = [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]

BUFFERVIEW_TARGET_ARRAY_BUFFER = 34962
BUFFERVIEW_TARGET_ELEMENT_ARRAY_BUFFER = 34963

PRIMITIVE_MODE_POINTS = 0
PRIMITIVE_MODE_LINES = 1
PRIMITIVE_MODE_LINE_LOOP = 2
PRIMITIVE_MODE_LINE_STRIP = 3
PRIMITIVE_MODE_TRIANGLES = 4
PRIMITIVE_MODE_TRIANGLE_STRIP = 5
PRIMITIVE_MODE_TRIANGLE_FAN = 6


class GLTFSpecObject(object):
    fields = []
    requiredFields = []

    def __init__(self):
        pass

    def __repr__(self):
        return json.dumps(self.gltf)

    @property
    def gltf(self):
        result = {}

        for field in self.fields:
            fieldValue = getattr(self, field, None)
            if fieldValue is not None:
                result[field] = fieldValue

            if field in self.requiredFields and field is None:
                logger.exception('Field is required for glTF {0}: {1}'.format(self.__name__, field))

        return result