import logging
import math

from maya.api import OpenMaya

import utils
from gltf.interface import core, gltf


def importGLTF(directory):
    logger = logging.getLogger(__name__)
    
    ctx = gltf.GLTF.importGLTF(directory)

    # logger.info(ctx.serialized())

    nodes = []

    for node in ctx.nodes:
        nodeFn = createTransform(node.name)
        nodes.append(nodeFn)

    for index, nodeMObject in enumerate(nodes):
        dagNode = OpenMaya.MFnDagNode(nodeMObject)

        gltfNode = ctx.nodes[index]
        if gltfNode.children is not None:
            for childMObject in [nodes[i] for i in gltfNode.children]:
                dagNode.addChild(childMObject)

    for index, nodeMObject in enumerate(nodes):
        mat = ctx.nodes[index].matrix
        if mat is not None:
            matFn = OpenMaya.MMatrix(mat)
            transformMatFn = OpenMaya.MTransformationMatrix(matFn)
            transformFn = OpenMaya.MFnTransform(nodeMObject)
            transformFn.setTransformation(transformMatFn)


def createTransform(name):
    return OpenMaya.MFnDagNode().create('transform', name)