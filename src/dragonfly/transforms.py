import logging

from maya.api import OpenMaya
from maya import cmds


LOG = logging.getLogger(__name__)


def getParentNodes(nodes):
    """Given a list of nodes, returns the top-most level nodes of the list.

    Returns:
        Union[list, OpenMaya.MObject]
    """
    result = []

    for n in nodes:
        if any([p in nodes for p in getAllParents(n)]):
            continue
        result.append(n)
    
    return result


def getAllParents(node):
    """Return all parents of the given node.

    Returns:
        Union[list, OpenMaya.MObject]
    """
    dagNode = OpenMaya.MFnDagNode(node)

    parentCount = dagNode.parentCount()
    
    parents = []
    
    for parentIndex in range(parentCount):
        parent = dagNode.parent(parentIndex)
        if not parent.hasFn(OpenMaya.MFn.kTransform):
            continue
    
    result = []
    
    if parents:
        result.append(parent)
        result.extend(getAllParents(parent))

    return result


def getAllChildTransforms(node):
    dagNode = OpenMaya.MFnDagNode(node)

    children = []

    for childIndex in range(dagNode.childCount()):
        child = dagNode.child(childIndex) 
        if not child.hasFn(OpenMaya.MFn.kTransform):
            continue
        children.append(child)

    result = []

    if children:
        for child in children:
            result.append(child)
            result.extend(getAllChildTransforms(child))

    return result


def getDagPaths(nodes):
    result = []

    for node in nodes:
        if node.hasFn(OpenMaya.MFn.kTransform):
            result.append(OpenMaya.MFnDagNode(node).getPath())

    return result


def freezeTree(node):
    """Freeze all transforms in the given node's hierarchy without affecting pivots.
    Does this by parenting all children to the world, freezing, then restoring the hierarchy.
    
    Returns:
        None
    """
    children = getAllChildTransforms(node)
    childrenPaths = getDagPaths(children)

    parentMap = [(c, OpenMaya.MFnDagNode(OpenMaya.MFnDagNode(c).parent(0)).getPath()) for c in childrenPaths]
    
    for c in childrenPaths:
        cmds.parent(c.fullPathName(), world=True)
    
    nodeDagPath = OpenMaya.MFnDagNode(node).getPath()

    for n in [nodeDagPath] + childrenPaths:
        cmds.makeIdentity(n.fullPathName(), t=0, r=0, s=1, n=0, apply=True)
    
    for pair in parentMap:
        cmds.parent(pair[0], pair[1])
