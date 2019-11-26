import logging

from maya.api import OpenMaya

import utils




class ExportNodeMap(object):
    """
    Schema:
        <nodeName>:
            object: OpenMaya.MObject
            parent: OpenMaya.MObject
            meshes:
                <meshName>:
                    object: OpenMaya.MObject
                    skin: OpenMaya.MObject
                    joints: Union[list, OpenMaya.MObject]
    """

    def __init__(self):
        pass


def exportSelection():
    """Select a transform object to export.
    
    Exports the related hierarchy, along with associated materials,
    textures, and animation data.
    """

    # Get the transform hierarchy as nested lists
    # Create a new dict with each objects fullpath as their key, and parent as the first value
    # From the transform hiearchy find all the shape nodes
    # With all the mesh shape nodes, split into 2 lists, static and skinned meshes
    # For static meshes get their vertex position and normal data
    # for skinned meshes find their joints

    logger = logging.getLogger(__name__)

    nodes = []

    for n in utils.getSelection():
        nodes.append(n)
        nodes.extend(utils.getChildren(n))

    allTransforms = [i for n, i in enumerate(nodes) if i not in nodes[:n]] 

    logger.info(allTransforms)

    hierarchyMap = {}

    for t in allTransforms:
        # Set object.
        fullName = utils.getNodePath(t)
        
        if fullName not in hierarchyMap:
            hierarchyMap[fullName] = {}

        hierarchyMap[fullName]['object'] = t

        # Set parent transform object.
        for parentMObject in utils.getParents(t):
            
            if parentMObject in allTransforms:
                hierarchyMap[fullName]['parent'] = parentMObject

        # Set mesh objects.
        shapeMObjects = utils.getMesh(t)
        for mesh in shapeMObjects:
            # Skip if the mesh is an intermediate mesh used for deformers.
            if utils.isIntermediateObject(mesh):
                continue
            
            # Create a mesh map in the node map.
            meshFullName = utils.getNodePath(mesh)
            
            if 'meshes' not in hierarchyMap[fullName]:
                hierarchyMap[fullName]['meshes'] = {}
            
            if meshFullName not in hierarchyMap[fullName]['meshes']:
                hierarchyMap[fullName]['meshes'][meshFullName] = {}
            
            hierarchyMap[fullName]['meshes'][meshFullName]['object'] = mesh

            # Set skin cluster object.
            skin = utils.getSkin(mesh)

            if skin is not None:
                hierarchyMap[fullName]['meshes'][meshFullName]['skin'] = skin

                # Set influence list with mesh.
                influences = utils.getSkinInfluences(skin)

                if 'joints' not in hierarchyMap[fullName]['meshes'][meshFullName]:
                    hierarchyMap[fullName]['meshes'][meshFullName]['joints'] = influences

                # Get entire skeleton, make sure each transform is in our hierarchy map.
                skeleton = utils.getSkeletonHierarchy(influences)

                for joint in skeleton:
                    jointDagNode = OpenMaya.MFnDagNode(joint)
                    jointFullName = jointDagNode.fullPathName()
                    
                    if jointFullName not in hierarchyMap:
                        hierarchyMap[jointFullName] = {}
                        hierarchyMap[jointFullName]['object'] = joint

    logger.info(hierarchyMap)