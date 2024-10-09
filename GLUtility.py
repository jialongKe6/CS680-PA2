try:
    import OpenGL

    try:
        import OpenGL.GL as gl
        import OpenGL.GLU as glu
    except ImportError:
        from ctypes import util

        orig_util_find_library = util.find_library


        def new_util_find_library(name):
            res = orig_util_find_library(name)
            if res:
                return res
            return '/System/Library/Frameworks/' + name + '.framework/' + name


        util.find_library = new_util_find_library
        import OpenGL.GL as gl
        import OpenGL.GLU as glu
except ImportError:
    raise ImportError("Required dependency PyOpenGL not present")

import math
import numpy as np


# used to handle the case when viewing dir is the same as upVector
# if that case is detected, to provide smooth view matrix, then use lastUpAxis as upVector
class GLUtility:
    lastUpAxis = None

    def __init__(self):
        self.lastUpAxis = np.array([0, 1, 0])

    def view(self, cameraPos, lookAtPoint, upVector, columnMajor=True):
        cameraPos = np.array(cameraPos)
        lookAtPoint = np.array(lookAtPoint)
        upVector = np.array(upVector)
        upVector = upVector / np.linalg.norm(upVector)
        viewingDir = cameraPos - lookAtPoint
        viewingDir = viewingDir / np.linalg.norm(viewingDir)
        # project upVector to the plane which perpendicular to viewingDir
        viewDotUp = np.dot(viewingDir, upVector)
        if (1 - abs(viewDotUp) < 1e-6) and (self.lastUpAxis is not None):
            # try to use lastUpAxis to fix this case
            upVector = self.lastUpAxis
            viewDotUp = np.dot(viewingDir, upVector)
        if 1 - abs(viewDotUp) < 1e-6:
            # if problem not solved by using lastUpAxis, use arbitrary vector
            upVector = np.array((1, 0, 0))
            viewDotUp = np.dot(viewingDir, upVector)

        # a vector perpendicular to viewing dir
        upAxis = upVector - viewDotUp / np.dot(viewingDir, viewingDir) * viewingDir
        upAxis = upAxis / np.linalg.norm(upAxis)
        self.lastUpAxis = upAxis

        xAxis = np.cross(upAxis, viewingDir)
        xAxis = xAxis / np.linalg.norm(xAxis)
        basisMatrix = np.identity(4)
        basisMatrix[0, 0:3] = xAxis
        basisMatrix[1, 0:3] = upAxis
        basisMatrix[2, 0:3] = viewingDir

        translateMatrix = self.translate(*(-cameraPos), columnMajor=False)

        viewMatrix = basisMatrix @ translateMatrix
        return viewMatrix.transpose() if columnMajor else viewMatrix

    @staticmethod
    def scale(xS, yS, zS, columnMajor=True):
        result = np.identity(4)
        result[0, 0] = xS
        result[1, 1] = yS
        result[2, 2] = zS
        return result.transpose() if columnMajor else result

    @staticmethod
    def perspective(fov, width, height, znear, zfar, columnMajor=True):
        """
        get perspective matrix of camera

        :param fov: FOV of camera, in deg
        :type fov: float
        :param width: screen width
        :type width: int
        :param height: screen height
        :type height: int
        :param znear: frustum z-near, cannot be zero
        :type znear: float
        :param zfar: frustum z-far
        :type zfar: float
        """
        znear = znear if znear != 0 else 0.001

        result = np.zeros((4, 4))
        halfRad = fov / 180 * math.pi * 0.5
        h = math.cos(halfRad) / math.sin(halfRad)
        w = h * height / width
        result[0, 0] = w
        result[1, 1] = h
        result[2, 2] = - (zfar + znear) / (zfar - znear)
        result[2, 3] = - (2 * zfar * znear) / (zfar - znear)
        result[3, 2] = -1
        return result.transpose() if columnMajor else result

    @staticmethod
    def translate(x, y, z, columnMajor=True):
        """
        4x4 homogeneous translation matrix
        """
        result = np.identity(4)
        result[0, 3] = x
        result[1, 3] = y
        result[2, 3] = z
        return result.transpose() if columnMajor else result

    @staticmethod
    def rotate(angle, rotationAxis, columnMajor=True):
        a = angle / 180 * math.pi

        sinHalfAngle = math.sin(0.5 * a)
        cosHalfAngle = math.cos(0.5 * a)

        s = cosHalfAngle
        a = sinHalfAngle * rotationAxis[0]
        b = sinHalfAngle * rotationAxis[1]
        c = sinHalfAngle * rotationAxis[2]

        # normalize
        norm = math.sqrt(s*s + a*a + b*b + c*c)
        if norm < 1e-6:
            return np.identity(4)
        s /= norm
        a /= norm
        b /= norm
        c /= norm

        result = np.zeros((4, 4))
        result[0, 0] = 1 - 2 * b * b - 2 * c * c
        result[1, 0] = 2 * a * b + 2 * s * c
        result[2, 0] = 2 * a * c - 2 * s * b
        result[0, 1] = 2 * a * b - 2 * s * c
        result[1, 1] = 1 - 2 * a * a - 2 * c * c
        result[2, 1] = 2 * b * c + 2 * s * a
        result[0, 2] = 2 * a * c + 2 * s * b
        result[1, 2] = 2 * b * c - 2 * s * a
        result[2, 2] = 1 - 2 * a * a - 2 * b * b
        result[3, 3] = 1

        return result.transpose() if columnMajor else result
