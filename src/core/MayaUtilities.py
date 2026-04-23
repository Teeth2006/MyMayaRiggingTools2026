import maya.cmds as mc
import maya.mel as ml
import maya.cmds as cmds
from maya.OpenMaya import MVector


def ConfiguredCtrlForjnt(jnt, ctrlName, doContraint=True):
  
    ctrlGrpName = ctrlName + "_grp"
    mc.group(ctrlName, n=ctrlGrpName)

    mc.matchTransform(ctrlGrpName, jnt)
    if doContraint:
        mc.orientConstraint(ctrlName, jnt)

    return ctrlName, ctrlGrpName

#make the plus shaped controller, this will be used for the ikfk blend
def CreatePlusController(namePrefix, radius, size=10):
    ctrlName = f"ac_{namePrefix}"
    ml.eval(f"curve -n {ctrlName} -d 1 -p 1 0 -1 -p 1 0 -3 -p -1 0 -3 -p -1 0 -1 -p -3 0 -1 -p -3 0 1 -p -1 0 1 -p -1 0 3 -p 1 0 3 -p 1 0 1 -p 3 0 1 -p 3 0 -1 -p 1 0 -1 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12")
    mc.setAttr(f"{ctrlName}.scale",size/6.0, size/6.0, size/6.0, type="double3")
    mc.makeIdentity(ctrlName, apply=True)
    
    target_obj ="CtrlName"
    attrs_to_hide = ["translateX","translateY","translateZ","scaleX","scaleY","scaleZ","rotateX","rotateY","rotateZ"]
     
    for attrs in attrs_to_hide:
     mc.setAttr(f"{ctrlName}.{attrs}",lock=True, keyable=False, channelBox=False)
    return ctrlName


    SetCurveLineWidth(ctrlName, 2)
    return ctrlName






def CreateCircleControllerForJnt(jnt, namePrefix, radius=10):
    ctrlName = f"ac{namePrefix}_{jnt}"
    mc.circle(n=ctrlName, r= radius, nr=(1,0,0))
    return ConfiguredCtrlForjnt(jnt, ctrlName)


def CreateBoxControllerForJnt(jnt, namePrefix, size=10):
    ctrlName = f"ac_{namePrefix}_{jnt}"
    ml.eval(f"curve -n {ctrlName}-d 1 -p 0.5 0.5 0.5 -p 0.5 0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 -0.5 0.5 -p -0.5 -0.5 0.5 -p -0.5 0.5 0.5 -p -0.5 -0.5 0.5 -p -0.5 -0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 -0.5 -0.5 -p 0.5 -0.5 -0.5 -p 0.5 0.5 -0.5 -p 0.5 -0.5 -0.5 -p 0.5 -0.5 0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15")
    mc.setAttr(f"{ctrlName}.scale",size, size, size, type="double3")
    
    #this is the same as freeze transformation command in maya
    mc.makeIdentity(ctrlName, apply=True)

    return ConfiguredCtrlForjnt(jnt, ctrlName)

def GetObjectPositionAsMVec(objectName):
   #t means translate values, ws means world space, q means query
   wsLoc = mc.xform(objectName, t= True, ws=True, q=True)
   return MVector(wsLoc[0], wsLoc[1], wsLoc[2])

def SetCurveLineWidth(curve, newWidth):
   shapes = mc.listRelatives(curve, s=True)
   for shape in shapes:
      mc.setAttr(f"{shape}.lineWidth", newWidth)