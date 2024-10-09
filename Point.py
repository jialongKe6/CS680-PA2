"""
A Point class is defined here, which stores point coordinates, color and corresponding texture coordinates.
First version Created on 09/23/2018

:author: micou(Zezhou Sun)
:version: 2021.1.3
"""
import copy
import time
import math
import numpy as np

from ColorType import ColorType


class Point:
    """
    Properties:
        coords: List<Integer>
        color: ColorType
        texture: List<Float>
    Desciption:
        Invisible Variables:
        coords is used to describe coordinates of a point, only integers allowed
        color is used to describe color of a point, must be ColorType Object
        texture is used to describe corresponding coordinates in texture, can be float or double
    """

    # Enforce type checking for all variables, set them invisible 
    coords = None
    color = None
    texture = None

    def __init__(self, coords=None, color=None, textureCoords=None):
        """
        init Point by using coords, __color, textureCoords or an existing point
        any missing argument will be set to all zero
        
        coords: list<int> or tuple<int>. 
        color: list or int or ColorType. 
        textureCoords: list or tuple.
        """
        # Be careful, Default dimension & dimensionT is 2
        self.setCoords(coords)
        self.setColor(color)
        self.setTextureCoords(textureCoords)

    def __repr__(self):
        return "p:" + str(self.getCoords()) + \
               " c:" + str(self.getColor()) + \
               " t:" + str(self.getTextureCoords())

    def __hash__(self):
        coords = self.coords
        if self.coords is None:
            coords = (None,)
        texture = self.texture
        if self.texture is None:
            texture = (None, )
        return hash((tuple(coords), self.color, tuple(texture)))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        else:
            return (self.coords == other.getCoords()).all() and \
                    self.texture == other.getTextureCoords() and \
                    self.color == other.getColor()

    def __iter__(self):
        return iter(self.coords)

    def __len__(self):
        return len(self.coords)

    def __getitem__(self, i):
        return self.coords[i]

    def __setitem__(self, i, value):
        self.coords[i] = value

    def __mul__(self, coefficient):
        return Point([coefficient * i for i in self.coords], self.color, self.texture)

    def __rmul__(self, coefficient):
        return self.__mul__(coefficient)

    def __add__(self, anotherPoint):
        return Point([i + j for i, j in zip(self.coords, anotherPoint.coords)], self.color, self.texture)

    def __sub__(self, anotherPoint):
        return Point([i - j for i, j in zip(self.coords, anotherPoint.coords)], self.color, self.texture)

    ################# Start of basic functions
    def normalize(self):
        """
        Normalize current point's coords, return a new Point object

        :rtype: Point
        """
        norm = np.linalg.norm(self.coords)
        if norm == 0:
            # if the coords is not set or when it is all zero, keep it as original and return
            return self.copy()
        coords = self.coords / norm
        return Point(coords)

    def norm(self):
        """
        get the norm of this Point's coords

        :rtype: float
        """
        if self.coords is not None:
            return np.linalg.norm(self.coords)
        else:
            return 0.0

    def dot(self, pt):
        """
        get the dot product between this Point and another Point

        :rtype: float
        """
        if (self.coords is None) or (pt.coords is None):
            raise Exception("Cannot do dot product between empty Points")
        if len(self.coords) != len(pt.coords):
            raise Exception("Cannot do dot product between Points with different size")

        # this float conversion is necessary, otherwise result will have type np.float32/np.int/np.float64
        # any other iterable variable multiplied with these types will be forced to convert to np.array type
        return float(np.dot(self.coords, pt.coords))

    def reflect(self, normal):
        """
        reflect the vector from origin to self.coords, normalPoint's coords is the normal of the plane that vector
        reflect with

        :param normal: contains the surface normal which self.coords reflect with
        :type normal: Point
        """
        n = copy.deepcopy(normal).normalize()
        if len(n.coords) != len(self.coords):
            raise Exception("Cannot reflect vector with normal which have different size")
        ndp = 2 * self.dot(n)
        return self - ndp * n

    def cross3d(self, anotherVector):
        """
        cross product the vector with another vector
        """
        if (self.coords is None) or (anotherVector.coords is None) or \
                (len(self.coords) != 3) or (len(anotherVector.coords) != 3):
            raise Exception("Error v argument for cross product 3D. Only accept 3 dimension Point")
        s = self.coords
        d = anotherVector.coords
        return Point((s[1]*d[2]-s[2]*d[1], s[2]*d[0]-s[0]*d[2], s[0]*d[1]-s[1]*d[0]))

    def setColor(self, color):
        """
        Set point color

        :param color: Point's color
        :type color: ColorType
        :return: None
        """
        self.color = copy.deepcopy(color)

    def setColor_r(self, r):
        self.color.r = r

    def setColor_g(self, g):
        self.color.g = g

    def setColor_b(self, b):
        self.color.b = b

    def getDim(self):
        """
        get point coordinates dimension
        :return: point coordinates dimension, which is a non-negative integer
        """
        if self.coords is not None:
            return len(self.coords)
        else:
            return 0

    def getDimT(self):
        """
        get point texture coordinates dimension
        :return: point texture coordinates dimension, which is a non-negative integer
        """
        if self.texture is not None:
            return len(self.texture)
        else:
            return 0

    def getCoords(self):
        return self.coords

    def getTextureCoords(self):
        return self.texture

    def getColor(self):
        return self.color

    def setCoords(self, coords):
        """Use a tuple/list to set all values in coords"""
        if coords is not None:
            self.coords = np.array(coords)
        else:
            self.coords = None

    def setTextureCoords(self, textureCoords):
        """Use a tuple/list of coords to set all values in textureCoords"""
        if textureCoords is not None:
            self.texture = np.array(textureCoords)
        else:
            self.texture = None

    def copy(self):
        newPoint = Point(copy.deepcopy(self.coords), copy.deepcopy(self.color), copy.deepcopy(self.texture))
        return newPoint

    ################# End of basic functions


if __name__ == "__main__":
    a = Point((1, 2))
    print(a)
    a.setColor(ColorType(0.5, 0.2, 0.3))
    print(a)
    a.setCoords([3, 4])
    print(a)
    a.setTextureCoords((2.22, 3.33))
    print("Point a: ", a)
    b = a.copy()
    print("Point copied from point a: ", b)
    try:
        print("Test for illegal v")
        c = Point((1.5, 4))
    except:
        print("Get Error")

    # Test for list<Point>
    pl = [Point((1, 3)), Point((2, 3)),
          Point((3, 5))]
    print(pl)

    # Test for set<Point>
    ps = set(pl)
    print(ps)
    ps.add(Point((1, 3), ColorType(1, 0, 1)))
    print(ps)
    ps.add(Point((1, 3), ColorType(0, 0, 0)))
    print(ps)

    t1 = time.time()
    [Point() for _ in range(500 * 500)]
    print(time.time() - t1)
    t1 = time.time()
    for _ in range(500 * 500):
        a = Point()
    print(time.time() - t1)
    t1 = time.time()
    for _ in range(500 * 500):
        a = ColorType()
    print(time.time() - t1)
