"""
Implements the Displayable class by providing import functions for .dae meshes

:author: micou(Zezhou Sun)
:version: 2021.1.1

Modified by Daniel Scrivener 07/22
"""

from Displayable import Displayable
from GLBuffer import VAO, VBO, EBO
import numpy as np
import ColorType
from collada import *

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


class DisplayableMesh(Displayable):
    vao = None
    vbo = None
    ebo = None
    shaderProg = None

    vertices = None  # array to store vertex information
    indices = None  # stores triangle indices to vertices

    defaultColor = None

    def __init__(self, shaderProg, scale, vertexData, indexData, color=ColorType.BLUE):
        """
        :param shaderProg: compiled shader program
        :type shaderProg: GLProgram
        :param scale: set of three scale factors to be applied to each vertex
        :type scale: list or tuple
        :param filename: .dae file to import
        :type filename: string
        :param color: vertex color to be applied uniformly
        :type color: ColorType
        """
        super(DisplayableMesh, self).__init__()
        assert(len(scale) == 3)

        self.defaultColor = np.array(color.getRGB())

        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()

        self.indices = indexData
        self.vertices = vertexData

        for i in range(len(self.vertices) // 11):
            i = i * 11
            self.vertices[i] = self.vertices[i] * scale[0]
            self.vertices[i + 1] = self.vertices[i + 1] * scale[1]
            self.vertices[i + 2] = self.vertices[i + 2] * scale[2]
            self.vertices[i + 5] = self.defaultColor[0]
            self.vertices[i + 6] = self.defaultColor[1]
            self.vertices[i + 7] = self.defaultColor[2]

    def draw(self):
        self.vao.bind()
        self.ebo.draw()
        self.vao.unbind()

    def initialize(self):
        """
        Remember to bind VAO before this initialization. If VAO is not bind, program might throw an error
        in systems that don't enable a default VAO after GLProgram compilation
        """
        self.vao.bind()
        self.vbo.setBuffer(self.vertices, 11)
        self.ebo.setBuffer(self.indices)
        
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexPos"),
                                  stride=11, offset=0, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexNormal"),
                                  stride=11, offset=3, attribSize=3) # unused
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexColor"),
                                  stride=11, offset=6, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexTexture"),
                                  stride=11, offset=9, attribSize=2) # unused


        self.vao.unbind()

