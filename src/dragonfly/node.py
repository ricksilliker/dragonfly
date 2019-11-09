from maya import cmds

def createNode(nodeType, name):
    n = Node.fromType(nodeType)
    n.rename(name)

    return n

class Node(object):
    def __init__(self, name):
        if not cmds.objExists(name):
            raise ValueError('Failed to create Node: {0}'.format(name))

        self._fullPath = cmds.ls(name, long=True, recursive=True)[0]

    @staticmethod
    def fromType(nodeType):
        n = cmds.createNode(nodeType)
        
        return Node(n)

    def rename(self, newName):
        cmds.rename(self._fullPath, newName)
        self._fullPath = cmds.ls(name, long=True, recursive=True)[0]


class Attribute(object):
    def __init__(self, attr):
        pass

    @property
    def fullName(self):
        return

    def connect(self, nodeAttr):
        cmds.connectAttr(self.fullName, nodeAttr.fullName)

