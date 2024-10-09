"""
Create a x, y, z coordinate on canvas
First version at 09/28/2021

:author: micou(Zezhou Sun)
:version: 2021.2.1
"""

from Component import Component
from Point import Point
import ColorType as Ct
from Shapes import Cube


class ModelAxes(Component):
    """
    Define our linkage model
    """

    components = None
    contextParent = None

    def __init__(self, parent, position, shaderProg, display_obj=None):
        super().__init__(position, display_obj)
        self.components = []
        self.contextParent = parent

        xAxis = Cube(Point((0,0,0)), shaderProg, [0.05, 0.05, 2], Ct.RED)
        xAxis.setDefaultAngle(90, xAxis.vAxis)
        yAxis = Cube(Point((0,0,0)), shaderProg, [0.05, 0.05, 2], Ct.GREEN)
        yAxis.setDefaultAngle(-90, yAxis.uAxis)
        zAxis = Cube(Point((0,0,0)), shaderProg, [0.05, 0.05, 2], Ct.BLUE)
        self.addChild(xAxis)
        self.addChild(yAxis)
        self.addChild(zAxis)

        self.components = [xAxis, yAxis, zAxis]

