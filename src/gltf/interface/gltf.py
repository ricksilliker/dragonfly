import array
import logging
import json
import base64
import os
import io

import core


class GLTF(object):
    def __init__(self):
        self.asset = None  # Must be an object/dictionary.
        self.extras = None  # Can be any json serializeable type.
        self.extensions = None  # Must be an object/dictionary.
        self.scene = 0
        self.scenes = []
        self.accessors = []
        self.bufferViews = []
        self.buffers = []
        self.animations = []
        self.images = []
        self.materials = []
        self.meshes = []
        self.nodes = []
        self.textures = []
        self.skins = []
        self.cameras = []
        self.samplers = []
        self.extensionsUsed = []
        self.extensionsRequired = []
    
    def __repr__(self):
        return self.serialized()

    def toGLTF(self):
        result = {}

        result['asset'] = self.asset.gltf
        result['accessors'] = [a.gltf for a in self.accessors]
        result['bufferViews'] = [b.gltf for b in self.bufferViews]
        result['buffers'] = [b.gltf for b in self.buffers]
        result['scene'] = self.scene
        result['scenes'] = [s.gltf for s in self.scenes]
        result['nodes'] = [n.gltf for n in self.nodes]
        result['meshes'] = [m.gltf for m in self.meshes]

        print result['meshes']

        for m in result['meshes']:
            print m
            for i, p in enumerate(m['primitives']):
                m['primitives'][i] = p.gltf

        print result

        return result

    def serialized(self):
        return json.dumps(self.toGLTF(), indent=4, separators=(',', ' : '), allow_nan=False)

    def addData(self, lst, componentType):
        data = GLTF.getBinDataFromList(lst, componentType)
        buffView = bufferView.BufferView.addBufferView(self.buffers[0], data)
        self.bufferViews.append(buffView)

        return len(self.bufferViews) - 1

    @staticmethod
    def getBinDataFromList(lst, componentType):
        logger = logging.getLogger(__name__)

        if componentType not in core.COMPONENT_TYPES:
            raise ValueError(
                'componentType must be one of the following: {0}'.format(
                    'BYTE, UNSIGNED_BYTE, SHORT, UNSIGNED_SHORT, UNSIGNED_INT, FLOAT'))

        if not isinstance(lst, (list, tuple)):
            raise TypeError('lst must be a list')

        componentType = core.COMPONENT_TYPE_CODES[core.COMPONENT_TYPES[componentType]]

        logger.info('Component type: {0}'.format(componentType))

        return array.array(componentType, lst).tostring()

    @staticmethod
    def exportGLTF(gltfObject, outputDirectory):

        if not os.path.exists(os.path.abspath(outputDirectory)):
            os.makedirs(os.path.abspath(outputDirectory), 0755)

        gltfFilePath = os.path.abspath(os.path.join(outputDirectory, 'out.gltf'))
        with io.open(gltfFilePath, mode='w+', encoding='utf8', newline='\n') as fp:
            fp.write(unicode(gltfObject.serialized()))
            fp.write(unicode("\n"))

        for buff in gltfObject.buffers:
            binFilePath = os.path.abspath(os.path.join(outputDirectory, buff.name))
            with io.open(binFilePath, 'wb') as fp:
                fp.write(buff.data)


class Asset(core.GLTFSpecObject):
    fields = ['copyright', 'version', 'minVersion', 'generator', 'extensions', 'extras']
    requiredFields = ['version']

    def __init__(self):
        # str
        self.copyright = None
        # str
        self.generator = None
        # str
        self.version = None  # required
        # str
        self.minVersion = None
        # dict
        self.extensions = None
        # any
        self.extras = None

    @property
    def gltf(self):
        if self.version is None:
            # Assume we are using glTF 2.0 if not declared.
            self.version = '2.0'

        return super(Asset, self).gltf


class Accessor(core.GLTFSpecObject):
    fields = ['bufferView', 'byteOffset', 'componentType', 'normalized', 'count', 'type', 'max', 'min', 'sparse', 'name', 'extensions', 'extras']
    requiredFields = ['componentType', 'count', 'type']

    def __init__(self):
        # int, >= 0
        self.bufferView = None
        # int, >= 0
        self.byteOffset = 0
        # int, must be one of the 6 COMPONENT_TYPE_* constants
        self.componentType = None  # required
        # bool
        self.normalized = False
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


class Buffer(core.GLTFSpecObject):
    fields = ['uri', 'byteLength', 'name', 'extensions', 'extras']
    requiredFields = ['byteLength']

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

    @property
    def gltf(self):
        self.byteLength = self.getByteLength()
        
        if self.name is None:
            self.name = 'out.bin'
        
        if self.uri is None:
            self.uri = 'out.bin'

        return super(Buffer, self).gltf

    def getByteLength(self):
        return len(self._data)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def index(self):
        return self._bufferIndex


class BufferView(core.GLTFSpecObject):
    fields = ['buffer', 'byteOffset', 'byteLength', 'byteStride', 'target', 'name', 'extensions', 'extras']
    requiredFields = ['buffer', 'byteLength']

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
        if not isinstance(buffer, Buffer):
            raise TypeError('buffer must be of type {0}'.format(buffer.Buffer))

        if not isinstance(buffer, Buffer):
            raise TypeError('buffer must be of type {0}'.format(buffer.Buffer))

        buffView = BufferView()
        buffView.buffer = buffer.index
        buffView.byteLength = len(binaryData)
        buffView.byteOffset = len(buffer.data)

        buffer.data += binaryData

        padding = (4 - (len(binaryData) % 4)) % 4
        buffer.data += b'\x00' * padding

        return buffView


class Scene(core.GLTFSpecObject):
    fields = ['nodes', 'name', 'extensions', 'extras']
    requiredFields = []

    def __init__(self):
        # Union[list, int], >= 0 per item
        self.nodes = None
        # str
        self.name = None
        # dict
        self.extensions = None
        # any
        self.extras = None


class Node(core.GLTFSpecObject):
    fields = ['camera', 'children', 'skin', 'mesh', 'matrix', 'translation', 'rotation', 'scale', 'weights', 'name', 'extensions', 'extras']
    requiredFields = []

    def __init__(self):
        # int >= 0
        self.camera = None
        # Union[list, int], >= 0 per item
        self.children = None
        # int >= 0
        self.skin = None
        # Union[list, float][16]
        self.matrix = None  # IDENTITY_MATRIX
        # int, >= 0
        self.mesh = None
        # Union[list, float][4]
        self.rotation = None  # [0,0,0,1]
        # Union[list, float][3]
        self.scale = None  # [1,1,1]
        # Union[list, float][3]
        self.translation = None  # [0,0,0]
        # Union[list, int]
        self.weights = None
        # str
        self.name = None
        # dict
        self.extensions = None
        # any
        self.extras = None

    @property
    def gltf(self):
        # Clean up matrix attributes if there is no transformation.
        if self.matrix is not None:
            if self.matrix == core.IDENTITY_MATRIX:
                self.matrix = None

        return super(Node, self).gltf

class Mesh(core.GLTFSpecObject):
    fields = ['primitives', 'weights', 'name', 'extensions', 'extras']
    requiredFields = ['primitives']

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


class Primitive(core.GLTFSpecObject):
    fields = ['attributes', 'indices', 'material', 'mode', 'targets', 'extensions', 'extras']
    requiredFields = ['attributes']

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

    @staticmethod
    def getIndicesComponentType(indicesList):
        logger = logging.getLogger(__name__)

        if not isinstance(indicesList, (list, tuple)):    
            logger.exception('This method only excepts list type arguments.')
            return 0

        if max(indicesList) < 255:
            typ = core.COMPONENT_TYPE_UNSIGNED_BYTE
        elif max(indicesList) < 65535:
            typ = core.COMPONENT_TYPE_UNSIGNED_SHORT
        elif max(indicesList) < 4294967295:
            typ = core.COMPONENT_TYPE_UNSIGNED_INT
        else:
            logger.exception('Could not match to a component type.')
            return 0
        
        return typ

    @staticmethod
    def indicesToBytes(data):
        if not isinstance(data, (list, tuple)):
            logger = logging.getLogger(__name__)
            logger.exception('This method only excepts list type arguments.')
            return ''

        typ = Primitive.getIndicesComponentType(data)

        # return struct.pack(typ, data)
        return array.array(core.COMPONENT_TYPE_CODES[typ], data).tostring()
        
    @staticmethod
    def positionsToBytes(data):
        if not isinstance(data, (list, tuple)):
            logger = logging.getLogger(__name__)
            logger.exception('This method only excepts list type arguments.')
            return ''

        return array.array(core.COMPONENT_TYPE_CODES[core.COMPONENT_TYPE_FLOAT], data).tostring()