from maya.api import OpenMaya


def getAllChild(node):
    dagNode = OpenMaya.MFnDagNode(node)

    children = []

    for childIndex in range(dagNode.childCount()):
        child = dagNode.child(childIndex) 
        if not child.hasFn(OpenMaya.MFn.kJoint):
            continue
        children.append(child)

    result = []

    if children:
        for child in children:
            result.append(child)
            result.extend(getAllChild(child))

    return result