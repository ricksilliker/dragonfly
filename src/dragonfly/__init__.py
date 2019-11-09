import platform
import logging

from maya import OpenMayaUI
from shiboken2 import wrapInstance
from PySide2 import QtWidgets, QtCore


def mayaMainWindow():
    """Get Maya's main window as a QWidget."""
    OpenMayaUI.MQtUtil.mainWindow()
    ptr = OpenMayaUI.MQtUtil.mainWindow()

    return wrapInstance(long(ptr), QtWidgets.QWidget)


class AbstractWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AbstractWidget, self).__init__(parent=parent)

    @staticmethod
    def run():
        """Creates an instance of the ProjectEditor and shows it in Maya's main view."""
        app = mayaMainWindow()
        widget = AbstractViewable(parent=app)
        if platform.system() == 'Darwin':
            # MacOS is special, and the QtCore.Qt.Window flag does not sort the windows properly,
            # so instead QtCore.Qt.Tool is used.
            widget.setWindowFlags(widget.windowFlags() | QtCore.Qt.Tool)
        # Center the widget with Maya's main window.
        widget.move(app.frameGeometry().center() - QtCore.QRect(QtCore.QPoint(), widget.sizeHint()).center())
        
        widget.show()