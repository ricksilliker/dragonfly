import logging


class Asset(object):
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

        result = {}

        for field in self.fields:
            fieldValue = getattr(self, field, None)
            if fieldValue is not None:
                result[field] = fieldValue

            if field in self.requiredFields and field is None:
                logger.exception('Field is required for glTF Asset: {0}'.format(field))

        return result