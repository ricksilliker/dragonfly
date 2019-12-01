import logging
import math

from maya.api import OpenMaya

import utils
from gltf.interface import core, gltf


class ExportContext(object):
    """
    Schema:
        <nodeName>:
            object: OpenMaya.MObject
            parent: OpenMaya.MObject
            meshes:
                <meshName>:
                    object: OpenMaya.MObject
                    skin: OpenMaya.MObject
                    joints: [OpenMaya.MObject]
    """

    def __init__(self):
        self._gltf = gltf.GLTF()


def exportSelection(exportContext=None):
    # hierarchy = getExportContext(selection=True)

    logger = logging.getLogger(__name__)

    ctx = gltf.GLTF()

    ctx.asset = gltf.Asset()

    ctx.buffers.append(gltf.Buffer())

    ctx.scenes.append(gltf.Scene())
    ctx.scenes[0].nodes = []
    ctx.scenes[0].name = utils.getSceneName()

    getExportForTransforms(ctx)
    getExportForMeshes(ctx)

    gltf.GLTF.exportGLTF(ctx, '/Users/ricksilliker/Desktop/testAsset')
        

def getExportForTransforms(gltfContext):
    logger = logging.getLogger(__name__)

    transforms = []
    for n in utils.getSelection():
        if n.hasFn(OpenMaya.MFn.kTransform):
            transforms.append(n)

    result = []
    getGLTFNodes(gltfContext, transforms, result)

    gltfContext.nodes = result

    # logger.info(result)


def getGLTFNodes(ctx, nodes, nodeList, parentIndex=None):
    for n in nodes:
        nodeIndex = getGLTFNode(ctx, n, nodeList, parentIndex)
        getGLTFNodes(ctx, utils.getChildren(n), nodeList, nodeIndex)


def getGLTFNode(ctx, mobject, nodeList, parentIndex=None):
    dagNode = OpenMaya.MFnDagNode(mobject)

    n = gltf.Node()
    n.name = dagNode.fullPathName()
    n.matrix = list(utils.getLocalMatrix(mobject))

    nodeList.append(n)

    nodeIndex = len(nodeList) - 1

    if parentIndex is not None:
        parentNode = nodeList[parentIndex]
        if parentNode.children is None:
            parentNode.children = []
        parentNode.children.append(nodeIndex)
    else:
        ctx.scenes[0].nodes.append(nodeIndex)

    return nodeIndex


def getExportForMeshes(gltfContext):
    logger = logging.getLogger(__name__)

    for nodeIndex, gltfNode in enumerate(gltfContext.nodes):
        nodeMObject = utils.getMObject(gltfNode.name)
        meshIndex = getGLTFMesh(gltfContext, nodeIndex)

    # logger.info(gltfContext)


def getGLTFMesh(ctx, nodeIndex):
    buff = ctx.buffers[0]

    n = ctx.nodes[nodeIndex]
    nodeMObject = utils.getMObject(n.name)
    meshes = utils.getMesh(nodeMObject)
    if meshes:
        m = gltf.Mesh()
        m.primitives = []

        ctx.meshes.append(m)
        
        n.mesh = len(ctx.meshes) - 1
        
        for meshMObject in meshes:
            # Skip meshes that are deformer source nodes.
            if utils.isIntermediateObject(meshMObject):
                continue

            prim = gltf.Primitive()
            prim.attributes = {}
            m.primitives.append(prim)

            meshFn = OpenMaya.MFnMesh(meshMObject)

            vertCount = meshFn.numVertices
            vertArray = [x for x in range(vertCount)]

            triCorrelation, triVertIds = meshFn.getTriangles()
            triCount = 0
            for t in triCorrelation:
                triCount += t
            indices = [x for x in range(triCount * 3)]

            mpoints = [meshFn.getPoint(i) for i in triVertIds]
            positions = []
            for index in indices:
                pt = mpoints[index]
                positions.extend([pt.x, pt.y, pt.z])

            # mesh indices accessor            
            indicesAccessor = gltf.Accessor()
            indicesAccessor.type = "SCALAR"
            indicesAccessor.componentType = gltf.Primitive.getIndicesComponentType(indices)
            indicesAccessor.count = len(indices)
            indicesAccessor.min = [min(indices)]
            indicesAccessor.max = [max(indices)]

            buffData = gltf.Primitive.indicesToBytes(indices)

            buffView = gltf.BufferView.addBufferView(buff, buffData)
            ctx.bufferViews.append(buffView)

            indicesAccessor.bufferView = len(ctx.bufferViews) - 1

            ctx.accessors.append(indicesAccessor)

            prim.indices = len(ctx.accessors) - 1

            # mesh prim position accessor
            positionAccessor = gltf.Accessor()
            positionAccessor.type = "VEC3"
            positionAccessor.componentType = core.COMPONENT_TYPE_FLOAT

            positionAccessor.count = len(indices)

            positionAccessor.min = [float('inf') for i in range(3)]
            positionAccessor.max = [-float('inf') for i in range(3)]

            for pt in mpoints:
                for i, c in enumerate(pt):
                    if i > 2:
                        continue

                    positionAccessor.min[i] = min(positionAccessor.min[i], c)
                    positionAccessor.max[i] = max(positionAccessor.max[i], c)

            buffData = gltf.Primitive.positionsToBytes(positions)
            buffView = gltf.BufferView.addBufferView(buff, buffData)
            ctx.bufferViews.append(buffView)

            positionAccessor.bufferView = len(ctx.bufferViews) - 1

            ctx.accessors.append(positionAccessor)

            prim.attributes['POSITION'] = len(ctx.accessors) - 1


            
            

# def getExportContext(selection=True):
#     """Select a transform object to export.
    
#     Exports the related hierarchy, along with associated materials,
#     textures, and animation data.
#     """

#     # Get the transform hierarchy as nested lists
#     # Create a new dict with each objects fullpath as their key, and parent as the first value
#     # From the transform hiearchy find all the shape nodes
#     # With all the mesh shape nodes, split into 2 lists, static and skinned meshes
#     # For static meshes get their vertex position and normal data
#     # for skinned meshes find their joints

#     logger = logging.getLogger(__name__)

#     nodes = []

#     for n in utils.getSelection():
#         nodes.append(n)
#         nodes.extend(utils.getChildren(n))

#     allTransforms = [i for n, i in enumerate(nodes) if i not in nodes[:n]]

#     logger.info(allTransforms)

#     hierarchyMap = {}

#     for t in allTransforms:
#         # Set object.
#         fullName = utils.getNodePath(t)
        
#         if fullName not in hierarchyMap:
#             hierarchyMap[fullName] = {}

#         hierarchyMap[fullName]['object'] = t

#         # Set parent transform object.
#         for parentMObject in utils.getParents(t):
            
#             if parentMObject in allTransforms:
#                 hierarchyMap[fullName]['parent'] = parentMObject

#         # Set mesh objects.
#         shapeMObjects = utils.getMesh(t)
#         for mesh in shapeMObjects:
#             # Skip if the mesh is an intermediate mesh used for deformers.
#             if utils.isIntermediateObject(mesh):
#                 continue
            
#             # Create a mesh map in the node map.
#             meshFullName = utils.getNodePath(mesh)
            
#             if 'meshes' not in hierarchyMap[fullName]:
#                 hierarchyMap[fullName]['meshes'] = {}
            
#             if meshFullName not in hierarchyMap[fullName]['meshes']:
#                 hierarchyMap[fullName]['meshes'][meshFullName] = {}
            
#             hierarchyMap[fullName]['meshes'][meshFullName]['object'] = mesh

#             # Set skin cluster object.
#             skin = utils.getSkin(mesh)

#             if skin is not None:
#                 hierarchyMap[fullName]['meshes'][meshFullName]['skin'] = skin

#                 # Set influence list with mesh.
#                 influences = utils.getSkinInfluences(skin)

#                 if 'joints' not in hierarchyMap[fullName]['meshes'][meshFullName]:
#                     hierarchyMap[fullName]['meshes'][meshFullName]['joints'] = influences

#                 # Get entire skeleton, make sure each transform is in our hierarchy map.
#                 skeleton = utils.getSkeletonHierarchy(influences)

#                 for joint in skeleton:
#                     jointDagNode = OpenMaya.MFnDagNode(joint)
#                     jointFullName = jointDagNode.fullPathName()
                    
#                     if jointFullName not in hierarchyMap:
#                         hierarchyMap[jointFullName] = {}
#                         hierarchyMap[jointFullName]['object'] = joint

#     logger.info(hierarchyMap)
#     return hierarchyMap