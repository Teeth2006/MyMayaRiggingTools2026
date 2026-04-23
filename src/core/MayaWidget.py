import maya.cmds as mc
from PySide6.QtWidgets import QWidget, QMainWindow
from PySide6.QtCore import Qt
import maya.OpenMayaUI as omui
from shiboken6 import wrapInstance

def GetMayaMaininWindow()->QMainWindow:
    mayaMainWindow = omui.MQtUtil.mainWindow()
    return wrapInstance(int(mayaMainWindow), QMainWindow)

def RemoveWidgetWithName(objectName):
    for widget in GetMayaMaininWindow().findChildren(QWidget, objectName):
        widget.deleteLater()


class MayaWidget(QWidget):
    def __init__(self):
        super().__init__(parent=GetMayaMaininWindow())
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle("Maya Widget")
        RemoveWidgetWithName(self.GetwidgetHash())
        self.setObjectName(self.GetwidgetHash())

    def GetwidgetHash(self):
        return"48fa2d87b4099a10f688693cfc0273637d1f2e3e7c444c4382b5a5eee6e69e07"

