import math
import logging

from maya.api import OpenMaya
from maya import cmds


LOG = logging.getLogger(__name__)


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


def getChildren(node):
    result = []

    dagNode = OpenMaya.MFnDagNode(node)

    for index in range(dagNode.childCount()):
        child = dagNode.child(index)
        if child.hasFn(OpenMaya.MFn.kJoint):
            result.append(child)

    return result


def packRotation(node, preserveChildren):
    wm, r, ra, jo = getMatrices(node)
    setRotationMatrices(node, jo, preserveChildren)


def getMatrices(node):
    nodeName = OpenMaya.MFnDagNode(node).getPath()

    r = cmds.getAttr('{0}.r'.format(nodeName))
    r = [math.radians(x) for x in r[0]]
    ra = cmds.getAttr('{0}.ra'.format(nodeName))
    ra = [math.radians(x) for x in ra[0]]
    jo = cmds.getAttr('{0}.jo'.format(nodeName))
    jo = [math.radians(x) for x in jo[0]]

    wm = OpenMaya.MMatrix(cmds.getAttr('{0}.wm'.format(nodeName)))
    pm = OpenMaya.MMatrix(cmds.getAttr('{0}.pm'.format(nodeName)))

    r = OpenMaya.MEulerRotation(*r).asMatrix() * pm
    ra = OpenMaya.MEulerRotation(*ra).asMatrix() * pm
    jo = OpenMaya.MEulerRotation(*jo).asMatrix() * pm

    return wm, r, ra, jo


def setRotationMatrices(node, orientMatrix, preserveChildren=True):
    if preserveChildren:
        children = getChildren(node)
        matrices = [getMatrices(j) for j in children]

    wm, r, ra, jo = getMatrices(node)
    r = OpenMaya.MMatrix()
    ra = orientMatrix * r.inverse() * jo.inverse()
    setMatrices(node, wm, r, ra, jo)

    if preserveChildren:
        for child, childm in zip(children, matrices):
            setMatrices(child, *childm)


def setMatrices(node, worldMatrix, rotationMatrix, rotateAxisMatrix, orientMatrix, translate=True, rotate=True):
    nodeName = OpenMaya.MFnDagNode(node).fullPathName()

    pim = OpenMaya.MMatrix(cmds.getAttr('{0}.pim'.format(nodeName)))

    matrix = worldMatrix * pim
    
    if rotate:
        wm, r, ra, jo = getMatrices(node)

        rEuler = OpenMaya.MTransformationMatrix(rotationMatrix).rotation()
        rEuler = [math.degrees(rEuler.x), math.degrees(rEuler.y), math.degrees(rEuler.z)]
        LOG.info(rEuler)

        raEuler = OpenMaya.MTransformationMatrix(rotateAxisMatrix).rotation()
        raEuler = [math.degrees(raEuler.x), math.degrees(raEuler.y), math.degrees(raEuler.z)]
        LOG.info(raEuler)

        joEuler = OpenMaya.MTransformationMatrix(orientMatrix * pim * r * pim).rotation()
        joEuler = [math.degrees(joEuler.x), math.degrees(joEuler.y), math.degrees(joEuler.z)]
        LOG.info(joEuler)

        cmds.setAttr(nodeName + '.r', *rEuler)
        cmds.setAttr(nodeName + '.ra', *raEuler)
        cmds.setAttr(nodeName + '.jo', *joEuler)
    
    if translate:
        t = [matrix.getElement(3, 0), matrix.getElement(3, 1), matrix.getElement(3, 2)]
        cmds.setAttr(nodeName + '.t', *t)