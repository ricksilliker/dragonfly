import array
import logging
import json

import accessor


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
    
    def toGLTF(self):
        result = {}

        result['asset'] = self.asset.gltf
        result['scene'] = self.scene
        result['scenes'] = [s.gltf for s in self.scenes]
        result['nodes'] = [n.gltf for n in self.nodes]

        return result

    def serialized(self):
        return json.dumps(self.toGLTF(), indent=4, separators=(',', ' : '), allow_nan=False)

    @staticmethod
    def getBinDataFromList(lst, componentType):
        logger = logging.getLogger(__name__)

        if componentType not in accessor.COMPONENT_TYPES:
            raise ValueError(
                'componentType must be one of the following: {0}'.format(
                    'BYTE, UNSIGNED_BYTE, SHORT, UNSIGNED_SHORT, UNSIGNED_INT, FLOAT'))

        if not isinstance(lst, (list, tuple)):
            raise TypeError('lst must be a list')

        componentType = accessor.COMPONENT_TYPE_CODES[COMPONENT_TYPES[componentType]]

        logger.info('Component type: {0}'.format(componentType))

        return array.array(componentType, lst).tobytes()

    @staticmethod
    def exportGLTF(gltfObject, outputDirectory):
        gltfFilePath = os.path.abspath(os.path.join(outputDirectory, 'out.gltf'))
        with open(gltfFilePath, 'w', encoding='utf8', newline='\n') as fp:
            file.write(gltfObject.serialized())
            file.write("\n")

        for buff in gltfObjects.buffers:
            binFilePath = os.path.abspath(os.path.join(outputDirectory, buff.name))
            with open(binFilePath, 'wb') as fp:
                fp.write(buff.data)