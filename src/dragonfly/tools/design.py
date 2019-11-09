import logging
import math
import platform

from maya.api import OpenMaya
from maya.api import OpenMayaUI as omui
from maya import OpenMayaUI, cmds
from shiboken2 import wrapInstance
from PySide2 import QtWidgets, QtCore

from dragonfly import transforms, joints


LOG = logging.getLogger(__name__)


def mayaMainWindow():
    """Get Maya's main window as a QWidget."""
    OpenMayaUI.MQtUtil.mainWindow()
    ptr = OpenMayaUI.MQtUtil.mainWindow()

    return wrapInstance(long(ptr), QtWidgets.QWidget)


class ToolBoxWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ToolBoxWidget, self).__init__(parent=parent)

        generalToolsWidget = GeneralToolsWidget()
        jointToolsWidget = JointToolsWidget()

        tabs = QtWidgets.QTabWidget()
        tabs.addTab(generalToolsWidget, generalToolsWidget.tabTitle)
        tabs.addTab(jointToolsWidget, jointToolsWidget.tabTitle)
        
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        mainLayout.addWidget(tabs)

    @staticmethod
    def run():
        """Creates an instance of the ProjectEditor and shows it in Maya's main view."""
        app = mayaMainWindow()
        widget = ToolBoxWidget(parent=app)
        if platform.system() == 'Darwin':
            # MacOS is special, and the QtCore.Qt.Window flag does not sort the windows properly,
            # so instead QtCore.Qt.Tool is used.
            widget.setWindowFlags(widget.windowFlags() | QtCore.Qt.Tool)
        # Center the widget with Maya's main window.
        widget.move(app.frameGeometry().center() - QtCore.QRect(QtCore.QPoint(), widget.sizeHint()).center())
        
        widget.show()


class GeneralToolsWidget(QtWidgets.QWidget):
    tabTitle = 'General'

    def __init__(self, parent=None):
        super(GeneralToolsWidget, self).__init__(parent=parent)

        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        self.freezeScalesButton = QtWidgets.QPushButton('Freeze Scales')
        mainLayout.addWidget(self.freezeScalesButton)

        self.freezePivotsButton = QtWidgets.QPushButton('Freeze Pivots')
        mainLayout.addWidget(self.freezePivotsButton)

        self.parentButton = QtWidgets.QPushButton('Parent')
        mainLayout.addWidget(self.parentButton)

        self.createOffsetButton = QtWidgets.QPushButton('Create Offset')
        mainLayout.addWidget(self.createOffsetButton)

        self.parentInOrderButton = QtWidgets.QPushButton('Parent In Order')
        mainLayout.addWidget(self.parentInOrderButton)

        self.selectChildrenButton = QtWidgets.QPushButton('Select Children')
        mainLayout.addWidget(self.selectChildrenButton)

        self.freezeScalesButton.clicked.connect(self.freezeScales)
        self.freezePivotsButton.clicked.connect(self.freezePivots)
        self.parentButton.clicked.connect(self.parentSelected)
        self.createOffsetButton.clicked.connect(self.createOffset)
        self.parentInOrderButton.clicked.connect(self.parentSelectedInOrder)
        self.selectChildrenButton.clicked.connect(self.selectChildren)


    def freezeScales(self):
        selectionList = OpenMaya.MGlobal.getActiveSelectionList()
        
        depNodes = []

        for index in range(selectionList.length()):
            depNodes.append(selectionList.getDependNode(index))

        topDepNodes = transforms.getParentNodes(depNodes)
        for t in topDepNodes:
            transforms.freezeTree(t)

        OpenMaya.MGlobal.setActiveSelectionList(selectionList)

    def freezePivots(self):
        selectionList = OpenMaya.MGlobal.getActiveSelectionList()

        for index in range(selectionList.length()):
            dagPath = selectionList.getDagPath(index)
            nodeTransform = OpenMaya.MFnTransform(dagPath)
            pos = nodeTransform.rotatePivot(OpenMaya.MSpace.kWorld)
            LOG.info([pos.x, pos.y, pos.z])

            nodeTransform.setTranslation(OpenMaya.MVector.kZeroVector, OpenMaya.MSpace.kObject)

            src = nodeTransform.rotatePivot(OpenMaya.MSpace.kWorld)

            parent = OpenMaya.MFnDagNode(dagPath).parent(0)
            if not parent.hasFn(OpenMaya.MFn.kTransform):
                dst = OpenMaya.MPoint(OpenMaya.MVector.kZeroVector)
            else:
                parentPath = OpenMaya.MFnDagNode(parent).getPath()
                dst = OpenMaya.MFnTransform(parentPath).rotatePivot(OpenMaya.MSpace.kWorld)

            nodeTransform.setTranslation(dst - src, OpenMaya.MSpace.kObject)

            cmds.makeIdentity(dagPath.fullPathName(), a=True, t=True)

            nodeTransform.setTranslation(OpenMaya.MVector(pos), OpenMaya.MSpace.kWorld)

            # cmds.move(
            #     pos.x,
            #     pos.y,
            #     pos.z,
            #     dagPath.fullPathName(),
            #     ws=True,
            #     a=True
            # )


    def parentSelected(self):
        selectionList = OpenMaya.MGlobal.getActiveSelectionList()

        if selectionList.length() == 0:
            return

        nodeNames = list(selectionList.getSelectionStrings())
        parent = selectionList.getDependNode(0)

        conflicts = []
        for index in range(1, selectionList.length()):
            node = selectionList.getDependNode(index)
            if OpenMaya.MFnDagNode(parent).hasParent(node):
                conflicts.append(node)
    
        if conflicts:
            tops = transforms.getParentNodes(conflicts)
            newParentParent = OpenMaya.MFnDagNode(transforms.getParent(tops[0]))
            cmds.parent(nodeNames[0], newParentParent.fullPathName())

        parent = nodeNames.pop(0)
        nodeNames.append(parent)

        try:
            cmds.parent(*nodeNames)
        except RuntimeError as err:
            LOG.exception('Parent relationship already setup.')


    def createOffset(self):
        selectionList = OpenMaya.MGlobal.getActiveSelectionList()

        for index in range(selectionList.length()):
            node = selectionList.getDependNode(index)
            nodePath = selectionList.getDagPath(index)
            
            offset = OpenMaya.MFnDependencyNode().create('transform')
            offsetPath = OpenMaya.MFnDagNode(offset).getPath()


            offsetTransform = OpenMaya.MFnTransform(offsetPath)
            nodeTransform = OpenMaya.MFnTransform(nodePath)

            ws = OpenMaya.MSpace.kWorld
            offsetTransform.setTranslation(nodeTransform.translation(ws), ws)
            offsetTransform.setRotation(nodeTransform.rotation(ws, asQuaternion=True), ws)
            offsetTransform.setScale(nodeTransform.scale())

            dagNode = OpenMaya.MFnDagNode(nodePath)
            parent = dagNode.parent(0)
            if parent.hasFn(OpenMaya.MFn.kTransform):
                cmds.parent(offsetPath.fullPathName(), OpenMaya.MFnDagNode(parent).fullPathName())
            
            cmds.parent(nodePath.fullPathName(), offsetPath.fullPathName())

    def parentSelectedInOrder(self):
        selectionList = OpenMaya.MGlobal.getActiveSelectionList()
        nodeNames = selectionList.getSelectionStrings()

        for nodeName in nodeNames:
            cmds.parent(nodeName, world=True)

        for index in reversed(range(1, selectionList.length())):
            parent = nodeNames[index - 1] 
            child = nodeNames[index]
            cmds.parent(child, parent)

    def selectChildren(self):
        selectionList = OpenMaya.MGlobal.getActiveSelectionList()
        
        newSelectionList = OpenMaya.MSelectionList()

        for index in range(selectionList.length()):
            depNode = selectionList.getDependNode(index)
            
            if depNode.hasFn(OpenMaya.MFn.kJoint):
                newSelectionList.add(depNode)
                for child in joints.getAllChild(depNode):
                    newSelectionList.add(child)

            if depNode.hasFn(OpenMaya.MFn.kTransform):
                newSelectionList.add(depNode)
                for child in transforms.getAllChildTransforms(depNode):
                    newSelectionList.add(child)

        for name in newSelectionList.getSelectionStrings():
            OpenMaya.MGlobal.selectByName(name, OpenMaya.MGlobal.kAddToList)

class JointToolsWidget(QtWidgets.QWidget):
    tabTitle = 'Joints'

    def __init__(self, parent=None):
        super(JointToolsWidget, self).__init__(parent=parent)

        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        self.createJointButton = QtWidgets.QPushButton('Joint Tool')
        mainLayout.addWidget(self.createJointButton)

        self.insertJointButton = QtWidgets.QPushButton('Insert Tool')
        mainLayout.addWidget(self.insertJointButton)
        
        self.centerJointButton = QtWidgets.QPushButton('Center')
        mainLayout.addWidget(self.centerJointButton)

        hLayout = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(hLayout)

        self.insertNumJointButton = QtWidgets.QPushButton('Insert')
        hLayout.addWidget(self.insertNumJointButton)
        self.insertNumJointField = QtWidgets.QSpinBox()
        hLayout.addWidget(self.insertNumJointField)

        self.toggleSSCButton = QtWidgets.QPushButton('Toggle SSC')
        mainLayout.addWidget(self.toggleSSCButton)

        self.createJointButton.clicked.connect(self.createNewJoint)
        self.insertJointButton.clicked.connect(self.insertNewJoint)
        self.centerJointButton.clicked.connect(self.centerSelectedJoint)
        self.insertNumJointButton.clicked.connect(self.insertNumJoints)
        self.toggleSSCButton.clicked.connect(self.toggleSSC)

    def createNewJoint(self):
        OpenMaya.MGlobal.executeCommandOnIdle('JointTool')

    def insertNewJoint(self):
        OpenMaya.MGlobal.executeCommandOnIdle('InsertJointTool')

    def centerSelectedJoint(self):
        """Center a joint between 2 other joints.

        Args:

        Returns:
            None
        """

        selectionList = OpenMaya.MGlobal.getActiveSelectionList()
        for index in range(selectionList.length()):
            mObject = selectionList.getDependNode(index)
            dagPath = selectionList.getDagPath(index)
            dagNode = OpenMaya.MFnDagNode(dagPath)

            if not mObject.hasFn(OpenMaya.MFn.kJoint):
                LOG.exception('Selected object is not a joint, skipping: {0}'.format(dagNode.fullPathName()))
                continue

            childCount = dagNode.childCount()
            if childCount == 0:
                LOG.exception('No children cannot center joint.')
                return

            parentCount = dagNode.parentCount()
            if parentCount == 0:
                LOG.exception('No parent cannot center joint.')
                return

            children = []
            for childIndex in range(childCount):
                childObject = dagNode.child(childIndex)
                if childObject.hasFn(OpenMaya.MFn.kJoint):
                    children.append(childObject)
            if not children:
                LOG.exception('No children are joints , cannot center joint.')
                return

            if parentCount > 1:
                LOG.exception('Joint is an instance, cannot center joint.')
                return
            
            if not dagNode.parent(0).hasFn(OpenMaya.MFn.kJoint):
                LOG.exception('Parent is not a joint, cannot center joint.')
                return

            parent = OpenMaya.MFnDagNode(dagNode.parent(0)).getPath()
            child = OpenMaya.MFnDagNode(children[0]).getPath()

            parentWorldPosition = OpenMaya.MFnTransform(parent).translation(OpenMaya.MSpace.kWorld)
            childWorldPosition = OpenMaya.MFnTransform(child).translation(OpenMaya.MSpace.kWorld)

            midPointVector = (parentWorldPosition + childWorldPosition) * 0.5

            cmds.move(
                midPointVector.x,
                midPointVector.y,
                midPointVector.z,
                dagPath.fullPathName(),
                pcp=True,
                ws=True
            )

    def insertNumJoints(self):
        count = self.insertNumJointField.value()
        selectionList = OpenMaya.MGlobal.getActiveSelectionList()
        for index in range(selectionList.length()):
            depNode = selectionList.getDependNode(index)
            dagPath = selectionList.getDagPath(index)
            dagNode = OpenMaya.MFnDagNode(dagPath)

            if not dagNode.parent(0).hasFn(OpenMaya.MFn.kTransform):
                LOG.exception('Parent is not a transform, cannot insert more joints.')
                return

            parent = OpenMaya.MFnDagNode(dagNode.parent(0)).getPath()
            parentWorldPosition = OpenMaya.MFnTransform(parent).translation(OpenMaya.MSpace.kWorld)

            jntWorldPosition = OpenMaya.MFnTransform(dagPath).translation(OpenMaya.MSpace.kWorld)

            joints = [parent]

            for i in range(count):
                position = (jntWorldPosition - parentWorldPosition) * (float(i+1)/float(count+1)) + parentWorldPosition

                # TODO: Maybe figure out if this can be undone?
                # newJointName = cmds.createNode('joint')
                # selList = OpenMaya.MSelectionList()
                # selList.add(newJointName)
                # newJoint = selList.getDependNode(0)
                newJoint = OpenMaya.MFnDependencyNode().create('joint')

                newJointPath = OpenMaya.MFnDagNode(newJoint).getPath()
                
                OpenMaya.MFnTransform(newJointPath).setTranslation(position, OpenMaya.MSpace.kWorld)

                cmds.parent(newJointPath.fullPathName(), joints[-1].fullPathName())
                cmds.joint(newJointPath.fullPathName(), e=True, oj='xyz', secondaryAxisOrient='yup', zso=True)

                joints.append(newJointPath)

            cmds.parent(dagPath.fullPathName(), joints[-1].fullPathName())


    def toggleSSC(self):
        selectionList = OpenMaya.MGlobal.getActiveSelectionList()
        for index in range(selectionList.length()):
            mObject = selectionList.getDependNode(index)
            depNode = OpenMaya.MFnDependencyNode(mObject)
            sscPlug = depNode.findPlug('segmentScaleCompensate', False)
            currentValue = sscPlug.asBool()
            sscPlug.setBool(not(currentValue))