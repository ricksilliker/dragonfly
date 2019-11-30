from maya import cmds
from maya.api import OpenMaya, OpenMayaAnim


def getChildren(node, recursive=True):
    result = []
    
    dagNode = OpenMaya.MFnDagNode(node)
    
    for i in range(dagNode.childCount()):
        childMObject = dagNode.child(i)

        if childMObject.hasFn(OpenMaya.MFn.kTransform):
            result.append(childMObject)
            if recursive:
                result.extend(getChildren(childMObject))

    return result


def getSelection(asDagPath=False):
    selectionList = OpenMaya.MGlobal.getActiveSelectionList()
    for i in range(selectionList.length()):
        if asDagPath:
            yield selectionList.getDagPath(i)
        else:
            yield selectionList.getDependNode(i)


def getMObject(nodeName):
    selectionList = OpenMaya.MSelectionList()
    selectionList.add(nodeName)

    return selectionList.getDependNode(0)


def getNodePath(node):
    dag = OpenMaya.MFnDagNode(node)
    
    return dag.fullPathName()


def getParents(node):
    dag = OpenMaya.MFnDagNode(node)

    for i in range(dag.parentCount()):
        yield dag.parent(i)


def getMesh(node):
    result = []

    dag = OpenMaya.MFnDagNode(node)
    
    for i in range(dag.childCount()):
        childMObject = dag.child(i)
    
        if childMObject.hasFn(OpenMaya.MFn.kMesh):
            result.append(childMObject)

    return result


def getSkin(node):
    skin = None
    
    iterDG = OpenMaya.MItDependencyGraph(
        node, 
        OpenMaya.MItDependencyGraph.kDownstream, 
        OpenMaya.MItDependencyGraph.kPlugLevel)
    
    while not iterDG.isDone():
        currentItem = iterDG.currentNode()
        
        if currentItem.hasFn(OpenMaya.MFn.kSkinClusterFilter):
            skin = currentItem
            break
        
        iterDG.next()

    return skin


def getSkinInfluences(node):
    skin = OpenMayaAnim.MFnSkinCluster(node)
    
    return [inf.node() for inf in skin.influenceObjects()]


def getSkeletonHierarchy(influences):
    nodes = getSkeleton(influences)

    return [i for n, i in enumerate(nodes) if i not in nodes[:n]] 


def getSkeleton(influences):
    result = []

    for n in influences:
        result.append(n)

        for parentMObject in getParents(n):
            
            if parentMObject.hasFn(OpenMaya.MFn.kTransform) and parentMObject not in influences:
                result.extend(getSkeleton([parentMObject]))

    return result


def isIntermediateObject(node):
    depNode = OpenMaya.MFnDependencyNode(node)
    ioPlug = depNode.findPlug('intermediateObject', False)
    
    return ioPlug.asBool()


def getSceneName():
    return cmds.file(q=True, sn=True, shn=True)


def getLocalMatrix(node):
    if not node.hasFn(OpenMaya.MFn.kTransform):
        return

    depNode = OpenMaya.MFnDependencyNode(node)
    localMatrixPlug = depNode.findPlug('matrix', False)
    matrixAttrMObject = localMatrixPlug.asMObject()
    matrixData = OpenMaya.MFnMatrixData(matrixAttrMObject)

    return matrixData.matrix()
