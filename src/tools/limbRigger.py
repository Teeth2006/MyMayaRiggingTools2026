from core.MayaWidget import MayaWidget # The of the UI class
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QColorDialog # Allows you to code out the pop up menu for the color picker
import maya. cmds as mc #Lets you create and control joints
from maya.OpenMaya import MVector # this is the same as the Vector3 in Unity, tranform position
import maya.cmds as cmds #same as mc
from PySide6.QtWidgets import QColorDialog #Imports the color picker
from PySide6.QtGui import QColor

import importlib # Allows updates without restarting Maya
import core.MayaUtilities #Imports functions 
importlib.reload(core.MayaUtilities) #
from core.MayaUtilities import (CreateCircleControllerForJnt, 
                                CreateBoxControllerForJnt,  
                                CreatePlusController, 
                                ConfiguredCtrlForjnt,
                                GetObjectPositionAsMVec
                                )

class LimbRigger:
    def __init__(self):
        self.nameBase = ""
        self.controllerSize = 10
        self.blendControllerSize = 4
        self.controlColorRGB = [0,0,0] #Creates attributes on an object and asigns the list of values for the color picker

    def SetNameBase(self, newNameBase):
        self.nameBase = newNameBase
        print(f"name base is set to: {self.nameBase}")

    def SetControllerSize(self, newControllerSize):
        self.controllerSize = newControllerSize

    def SetBlendCOntrollerSize(self, newBlendControllerSize):
        self.blendControllerSize = newBlendControllerSize

    def RigLimb(self):
        print("Start rigging!!")
        rootJnt, midJnt, endJnt = mc.ls(sl=True)
        print(f"found root {rootJnt}, mid: {midJnt} and end: {endJnt}") 

        rootCtrl, rootCtrlGrp = CreateCircleControllerForJnt(rootJnt,"fk_" + self.nameBase,self.controllerSize)
        midCtrl, midCtrlGrp = CreateCircleControllerForJnt(midJnt,"fk_" + self.nameBase, self.controllerSize)
        endCtrl, endCtrlGrp = CreateCircleControllerForJnt(endJnt,"fk_" + self.nameBase, self.controllerSize) 

        mc.parent(endCtrlGrp, midCtrl)
        mc.parent(midCtrlGrp, rootCtrl)

        endikCtrl, endIkCtrlGrp = CreateBoxControllerForJnt(endJnt, "ik_"+ self.nameBase, self.controllerSize)
        IkFkBlend=  CreatePlusController("ik_"+ self.nameBase, self.controllerSize)

        ikfkBlendCtrlPrefix = self.nameBase + "_ikfkBlend"
        ikFkBlendContrllor= CreatePlusController(ikfkBlendCtrlPrefix, self.blendControllerSize)
        ikFkBlendContrllor,  ikFkBlendControllerGrp = ConfiguredCtrlForjnt(rootJnt, ikFkBlendContrllor, False)

        ikfkBlendAttrName = "ikfkBlend"
        mc.addAttr(ikFkBlendContrllor, ln=ikfkBlendAttrName, min=0, max=1, k=True)

        ikHandleName = "ikHandle_" + self.nameBase
        mc.ikHandle(n=ikHandleName, sj = rootJnt, ee=endJnt, sol="ikRPsolver")

        rootJntLoc = GetObjectPositionAsMVec(rootJnt)
        endJntLoc = GetObjectPositionAsMVec (endJnt)
        poleVectorsVals = mc.getAttr(f"{ikHandleName}.poleVector")[0]
        poleVecDir = MVector(poleVectorsVals[0], poleVectorsVals[1], poleVectorsVals[2])
        poleVecDir.normalize() # make it a unit vector, a vector that has a length of 1

        rootToEndVec: MVector = endJntLoc - rootJntLoc
        rootToEndDist = rootToEndVec.length()

        

        poleVectorCtrlLoc = rootJntLoc + rootToEndVec/2.0 + poleVecDir * rootToEndDist

        poleVectorCtrlName = "ac_ik_" + self.nameBase + "poleVector"
        mc.spaceLocator(n=poleVectorCtrlName)

        poleVectorCtrlGrpName = poleVectorCtrlName + "_grp"
        mc.group(poleVectorCtrlName, n = poleVectorCtrlGrpName)

        mc.setAttr(f"{poleVectorCtrlGrpName}.translate",poleVectorCtrlLoc.x, poleVectorCtrlLoc.y, poleVectorCtrlLoc.z, type="double3")
        mc.poleVectorConstraint(poleVectorCtrlName, ikHandleName)

        mc.parent(ikHandleName, endikCtrl)
        mc.setAttr(f"{ikHandleName}.v",0)

        mc.connectAttr(f"{ikFkBlendContrllor}.{ikfkBlendAttrName}", f"{ikHandleName}.ikBlend")
        mc.connectAttr(f"{ikFkBlendContrllor}.{ikfkBlendAttrName}", f"{endIkCtrlGrp}.v")
        mc.connectAttr(f"{ikFkBlendContrllor}.{ikfkBlendAttrName}", f"{poleVectorCtrlGrpName}.v")

        reverseNodeName = f"{self.nameBase}_reverse"
        mc.createNode("reverse", n=reverseNodeName)

        mc.connectAttr(f"{ikFkBlendContrllor}.{ikfkBlendAttrName}", f"{reverseNodeName}.inputX")
        mc.connectAttr(f"{reverseNodeName}.outputX", f"{rootCtrlGrp}.v")



        orientConstaint = None 
        wristConnections = mc.listConnections(endJnt)
        for connection in wristConnections:
            if mc.objectType(connection) == "orientConstraint":
                orientConstaint = connection
                break


        mc.connectAttr(f"{ikFkBlendContrllor}.{ikfkBlendAttrName}", f"{orientConstaint}. {endikCtrl}W1")
        mc.connectAttr(f"{reverseNodeName}.outputX", f"{orientConstaint}.{endCtrl}W0")

        topGrpName = f"{self.nameBase}_rig_grp"
        mc.group(n=topGrpName, empty=True)

        mc.parent(rootCtrlGrp, topGrpName)
        mc.parent(ikFkBlendControllerGrp, topGrpName)
        mc.parent(endIkCtrlGrp, topGrpName)
        mc.parent(poleVectorCtrlGrpName, topGrpName)

        # Allows you to pick a custom color for the control rig
        mc.setAttr(f"{topGrpName}.overrideEnabled", 1)
        mc.setAttr(f"{topGrpName}.overrideRGBColors", 1)

        r, g, b = self.controlColorRGB
        mc.setAttr(f"{topGrpName}.overrideColorRGB", r, g, b)

        self.ApplyColorToCtrl(topGrpName)


class LimbRiggerWidget(MayaWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Limb Rigger")
        self.rigger = LimbRigger()
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.masterLayout.addWidget(QLabel("Select the 3 joints of the limb, from base to end, and then:"))

        self.infoLayout = QHBoxLayout()
        self.masterLayout.addLayout(self.infoLayout)
        self.infoLayout.addWidget(QLabel("Name Base:"))
        
        self.namebaseLineEdit = QLineEdit()
        self.infoLayout.addWidget(self.namebaseLineEdit)

        self.setNameBaseBtn = QPushButton("Set Name Base")
        self.setNameBaseBtn.clicked.connect(self.SetNameBaseClicked)
        self.infoLayout.addWidget(self.setNameBaseBtn)

        # This code creates a button to be made for the color picker
        self.colorBtn = QPushButton()
        self.colorBtn.setFixedSize(300,30)
        self.colorBtn.setStyleSheet("background-color: #ffffff;")
        self.masterLayout.addWidget(self.colorBtn)
        self.colorBtn.clicked.connect(self.ColorPicker)

    
        self.rigLimbBtn = QPushButton ("Rig Limb")
        self.rigLimbBtn.clicked.connect(self.RigLimbBtnClicked)
        self.masterLayout.addWidget(self.rigLimbBtn)

    def SetNameBaseClicked(self):
        self.rigger.SetNameBase(self.namebaseLineEdit.text())

    def RigLimbBtnClicked(self):
        self.rigger.RigLimb()

    def GetwidgetHash(self):
        return "3bd088cbd5bbb84b2e8b9d241d8f80e934c018f1dd3de2578cbe5021d623f706"

      #This code connects to the Maya color picker system
    def ColorPicker(self): 
        color = QColorDialog.getColor(parent=self)

        if color.isValid():
            r = color.red() / 255.0
            g = color.green() /255.0
            b = color.blue() /255.0

            self.rigger.controlColorRGB = [r, g, b] 

            self.colorBtn.setStyleSheet(f"background-color: rgb({color.red()},{color.green()},{color.blue()});") 

        
    

def Run():
    limbRiggerWidget = LimbRiggerWidget()
    limbRiggerWidget.show()

Run()