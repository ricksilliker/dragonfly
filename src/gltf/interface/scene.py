class Scene(object):
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

    @property
    def gltf(self):
        result = {}

        for field in self.fields:
            fieldValue = getattr(self, field, None)
            if fieldValue is not None:
                result[field] = fieldValue

            if field in self.requiredFields and field is None:
                logger.exception('Field is required for glTF Scene: {0}'.format(field))

        return result