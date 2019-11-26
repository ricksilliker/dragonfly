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

