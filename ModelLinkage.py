"""
Model our creature and wrap it in one class.
First version on 09/28/2021

:author: micou(Zezhou Sun)
:version: 2021.2.1

----------------------------------

Modified by Daniel Scrivener 09/2023
"""

from Component import Component
from Point import Point
import ColorType as Ct
from Shapes import Cube
from Shapes import Cone
from Shapes import Cylinder
from Shapes import Sphere
import numpy as np


class ModelLinkage(Component):
    """
    Define our linkage model
    """

    ##### TODO 2: Model the Creature
    # Build the class(es) of objects that could utilize your built geometric object/combination classes. E.g., you could define
    # three instances of the cyclinder trunk class and link them together to be the "limb" class of your creature.
    #
    # In order to simplify the process of constructing your model, the rotational origin of each Shape has been offset by -1/2 * dz,
    # where dz is the total length of the shape along its z-axis. In other words, the rotational origin lies along the smallest
    # local z-value rather than being at the translational origin, or the object's true center.
    #
    # This allows Shapes to rotate "at the joint" when chained together, much like segments of a limb.
    #
    # In general, you should construct each component such that it is longest in its local z-direction:
    # otherwise, rotations may not behave as expected.
    #
    # Please see Blackboard for an illustration of how this behavior works.

    components = None
    contextParent = None

    def __init__(self, parent, position, shaderProg, display_obj=None):
        super().__init__(position, display_obj)
        self.contextParent = parent

        linkageLength = 0.5
        link1 = Cube(
            Point((0, 0, 0)),
            shaderProg,
            [0.2, 0.2, linkageLength],
            Ct.DARKORANGE1,
        )
        link2 = Cube(
            Point((0, 0, linkageLength)),
            shaderProg,
            [0.2, 0.2, linkageLength],
            Ct.DARKORANGE2,
        )
        link3 = Cube(
            Point((0, 0, linkageLength)),
            shaderProg,
            [0.2, 0.2, linkageLength],
            Ct.DARKORANGE3,
        )
        link4 = Cube(
            Point((0, 0, linkageLength)),
            shaderProg,
            [0.2, 0.2, linkageLength],
            Ct.DARKORANGE4,
        )

        self.addChild(link1)
        link1.addChild(link2)
        link2.addChild(link3)
        link3.addChild(link4)

        self.componentList = [link1, link2, link3, link4]
        self.componentDict = {
            "link1": link1,
            "link2": link2,
            "link3": link3,
            "link4": link4,
        }

        ##### TODO 4: Define creature's joint behavior
        # Requirements:
        #   1. Set a reasonable rotation range for each joint,
        #      so that creature won't intersect itself or bend in unnatural ways
        #   2. Orientation of joint rotations for the left and right parts should mirror each other.


class Tail(Component):
    """
    Define our linkage model
    """

    components = None
    contextParent = None

    def __init__(self, parent, position, shaderProg, display_obj=None):
        super().__init__(position, display_obj)
        self.contextParent = parent

        linkageLength = 0.5
        self.link1 = Sphere(
            Point((0, 0, 0)),
            shaderProg,
            [0.2, 0.2, linkageLength],
            Ct.YELLOW,
        )
        self.link2 = Sphere(
            Point((0, 0, linkageLength * 2 - 0.1)),
            shaderProg,
            [0.2, 0.2, linkageLength],
            Ct.BLACK,
        )
        self.link3 = Sphere(
            Point((0, 0, linkageLength * 2 - 0.1)),
            shaderProg,
            [0.2, 0.2, linkageLength],
            Ct.YELLOW,
        )
        self.link4 = Sphere(
            Point((0, 0, linkageLength * 2 - 0.1)),
            shaderProg,
            [0.2, 0.2, linkageLength],
            Ct.BLACK,
        )
        self.needle = Cone(
            Point((0, 0, 1.5 * linkageLength)),
            shaderProg,
            [0.16, 0.16, linkageLength],
            Ct.NAVY,
        )

        self.link1.setDefaultAngle(-20, self.link1.uAxis)
        self.link2.setDefaultAngle(-60, self.link2.uAxis)
        self.link3.setDefaultAngle(-70, self.link3.uAxis)
        self.link4.setDefaultAngle(-30, self.link4.uAxis)
        self.needle.setDefaultAngle(-20, self.needle.uAxis)

        self.addChild(self.link1)
        self.link1.addChild(self.link2)
        self.link2.addChild(self.link3)
        self.link3.addChild(self.link4)
        self.link4.addChild(self.needle)

        self.componentList: list[Component | Sphere | Cone] = [
            self.link1,
            self.link2,
            self.link3,
            self.link4,
            self.needle,
        ]
        self.componentDict: dict[str, Sphere | Cone] = {
            "link1": self.link1,
            "link2": self.link2,
            "link3": self.link3,
            "link4": self.link4,
            "needle": self.needle,
        }

    def reset(self, mode="all"):
        self.link1.setDefaultAngle(-20, self.link1.uAxis)
        self.link2.setDefaultAngle(-60, self.link2.uAxis)
        self.link3.setDefaultAngle(-70, self.link3.uAxis)
        self.link4.setDefaultAngle(-30, self.link4.uAxis)
        self.needle.setDefaultAngle(-20, self.needle.uAxis)
        super().reset(mode)

        self.needle.setCurrentColor(Ct.NAVY)

    def setCurrentColor(self, color):
        self.needle.setCurrentColor(color)
        super().setCurrentColor(color)

    def resetColor(self):
        self.needle.setCurrentColor(Ct.NAVY)


class Legs(Component):
    """
    Define our linkage model
    """

    components = None
    contextParent = None

    def __init__(self, parent, position, shaderProg, display_obj=None):
        super().__init__(position, display_obj)
        self.contextParent = parent

        linkageLength = 0.5
        self.link1 = Cylinder(
            Point((0, 0, 0)),
            shaderProg,
            [0.1, 0.1, linkageLength],
            Ct.NAVY,
        )
        self.link2 = Cylinder(
            Point((0, 0, 3 * linkageLength - 0.01)),
            shaderProg,
            [0.1, 0.1, linkageLength * 2],
            Ct.BLACK,
        )
        self.link3 = Cylinder(
            Point((0, 0, 2.5 * linkageLength - 0.01)),
            shaderProg,
            [0.1, 0.1, linkageLength * 0.5],
            Ct.NAVY,
        )

        self.link1.setDefaultAngle(-50, self.link1.uAxis)
        self.link2.setDefaultAngle(100, self.link2.uAxis)
        self.link3.setDefaultAngle(-40, self.link3.uAxis)

        self.addChild(self.link1)
        self.link1.addChild(self.link2)
        self.link2.addChild(self.link3)

        self.componentList = [self.link1, self.link2, self.link3]
        self.componentDict = {
            "link1": self.link1,
            "link2": self.link2,
            "link3": self.link3,
        }

    def reset(self, mode="all"):
        self.link1.setDefaultAngle(-50, self.link1.uAxis)
        self.link2.setDefaultAngle(100, self.link2.uAxis)
        self.link3.setDefaultAngle(-40, self.link3.uAxis)
        super().reset(mode)


class Tooth(Component):
    """
    Define our linkage model
    """

    components = None
    contextParent = None

    def __init__(self, parent, position, size, shaderProg, display_obj=None):
        super().__init__(position, display_obj)
        self.contextParent = parent

        tooth = Cone(
            Point(position),
            shaderProg,
            # [0.05, 0.05, 0.25],
            size,
            Ct.YELLOW,
        )

        self.addChild(tooth)

        self.componentList = [tooth]
        self.componentDict = {"tooth": tooth}


class Eye(Component):
    """
    Define our linkage model
    """

    components = None
    contextParent = None

    def __init__(self, parent, position, shaderProg, display_obj=None):
        super().__init__(position, display_obj)
        self.contextParent = parent

        self.eye = Sphere(Point((0, 0, 0)), shaderProg, [0.1] * 3, Ct.NAVY)

        self.pupil = Sphere(Point((0, 0, 0.09)), shaderProg, [0.02] * 3, Ct.WHITE)

        self.addChild(self.eye)
        self.eye.addChild(self.pupil)

        self.componentList = [self.eye, self.pupil]
        self.componentDict = {"eye": self.eye, "pupil": self.pupil}


class Head(Component):
    """
    Define our linkage model
    """

    components = None
    contextParent = None

    def __init__(self, parent, position, shaderProg, display_obj=None):
        super().__init__(position, display_obj)
        self.contextParent = parent

        self.head = Sphere(
            Point((0, 0, 0)),
            shaderProg,
            [1, 0.5, 0.5],
            Ct.BLACK,
        )

        eyeballSize = 0.1
        leftEye = Eye(
            self,
            Point((0.3, 0.1, 0.45)),
            shaderProg,
        )
        # Sphere(
        #     Point((0.3, 0.1, 0.45)),
        #     shaderProg,
        #     [eyeballSize] * 3,
        #     Ct.NAVY,
        # )

        rightEye = Eye(
            self,
            Point((-0.3, 0.1, 0.45)),
            shaderProg,
        )
        # Sphere(
        #     Point((-0.3, 0.1, 0.45)),
        #     shaderProg,
        #     [eyeballSize] * 3,
        #     Ct.NAVY,
        # )

        self.leftTooth = Tooth(
            self,
            Point((0.1, -0.1, 0.3)),
            [0.05, 0.05, 0.25],
            shaderProg,
        )

        self.leftTooth.setDefaultAngle(-20, self.leftTooth.vAxis)

        self.rightTooth = Tooth(
            self,
            Point((-0.1, -0.1, 0.3)),
            [0.05, 0.05, 0.25],
            shaderProg,
        )
        self.rightTooth.setDefaultAngle(20, self.rightTooth.vAxis)

        self.addChild(self.head)
        self.head.addChild(leftEye)
        self.head.addChild(rightEye)
        self.head.addChild(self.leftTooth)
        self.head.addChild(self.rightTooth)

        self.componentList = [
            self.head,
            leftEye,
            rightEye,
            self.leftTooth,
            self.rightTooth,
        ]
        self.componentDict: dict[str, Component | Tooth] = {
            "head": self.head,
            "leftEye": leftEye,
            "rightEye": rightEye,
            "leftTooth": self.leftTooth,
            "rightTooth": self.rightTooth,
        }

    def reset(self, mode="all"):
        self.leftTooth.setDefaultAngle(-20, self.leftTooth.vAxis)
        self.rightTooth.setDefaultAngle(20, self.rightTooth.vAxis)
        super().reset(mode)

        self.head.setCurrentColor(Ct.BLACK)

    def setCurrentColor(self, color):
        self.head.setCurrentColor(color)
        super().setCurrentColor(color)

    def resetColor(self):
        self.head.setCurrentColor(Ct.BLACK)


class Body(Component):
    """
    Define our linkage model
    """

    components = None
    contextParent = None

    def __init__(self, parent, position, shaderProg, display_obj=None):
        super().__init__(position, display_obj)
        self.contextParent = parent

        self.xSize = 0.7
        self.ySize = 0.7
        self.zSize = 1
        self.body = Sphere(
            Point((0, 0, 0)),
            shaderProg,
            [self.xSize, self.ySize, self.zSize],
            Ct.BLACK,
        )

        self.leftLegs: dict[str, Legs] = {
            "leftLeg1": Legs(self, Point((self.xSize, 0, -0.5)), shaderProg),
            "leftLeg2": Legs(self, Point((self.xSize, 0, 0.0)), shaderProg),
            "leftLeg3": Legs(self, Point((self.xSize, 0, 0.5)), shaderProg),
        }

        for leg, offset in zip(self.leftLegs.values(), [20, 0, -20]):
            leg.setDefaultAngle(90 + offset, leg.vAxis)

        self.rightLegs: dict[str, Legs] = {
            "rightLeg1": Legs(self, Point((-self.xSize, 0, -0.5)), shaderProg),
            "rightLeg2": Legs(self, Point((-self.xSize, 0, 0.0)), shaderProg),
            "rightLeg3": Legs(self, Point((-self.xSize, 0, 0.5)), shaderProg),
        }

        for leg, offset in zip(self.rightLegs.values(), [20, 0, -20]):
            leg.setDefaultAngle(-90 - offset, leg.vAxis)

        self.addChild(self.body)
        for component in (self.leftLegs | self.rightLegs).values():
            self.addChild(component)

        self.componentList = [
            self.body,
            *list(self.leftLegs.values()),
            *list(self.rightLegs.values()),
        ]
        self.componentDict = {
            "head": self.body,
        } | (self.leftLegs | self.rightLegs)

    def reset(self, mode="all"):

        for leg, offset in zip(self.leftLegs.values(), [20, 0, -20]):
            leg.setDefaultAngle(90 + offset, leg.vAxis)

        for leg, offset in zip(self.rightLegs.values(), [20, 0, -20]):
            leg.setDefaultAngle(-90 - offset, leg.vAxis)

        for legs in (self.leftLegs | self.rightLegs).values():
            legs.reset(mode)
        super().reset(mode)

        self.body.setCurrentColor(Ct.BLACK)

    def setCurrentColor(self, color):
        self.body.setCurrentColor(color)
        super().setCurrentColor(color)

    def resetColor(self):
        self.body.setCurrentColor(Ct.BLACK)


class Spider(Component):
    """
    Define our linkage model
    """

    components = None
    contextParent = None

    def __init__(self, parent, position, shaderProg, display_obj=None):
        super().__init__(position, display_obj)
        self.contextParent = parent

        self.initPos = position
        body = Body(self, Point((0, 0, 0)), shaderProg)
        head = Head(self, Point((0, 0, body.zSize)), shaderProg)
        tail = Tail(self, Point((0, 0, -body.zSize)), shaderProg)

        body.vRange = [-15, 15]
        body.uRange = [-10, 10]
        body.wRange = [-10, 10]

        tail.setDefaultAngle(180, tail.vAxis)
        tail.uRange = [-30, 30]
        tail.vRange = [150, 230]
        tail.wRange = [-5, 5]

        self.addChild(body)
        self.addChild(head)
        self.addChild(tail)

        self.componentList = [head, body, tail]
        self.componentDict = {"head": head, "tail": tail, "body": body}
