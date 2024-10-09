"""
Define some classes and help methods to set up VAO, VBO, EBO
First version in 10/20/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""
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

import numpy as np
import ctypes


class VBO:
    """
    A class to set up VBO in OpenGL, with some help functions.
    """
    vbo = None
    vertexAttribSize = 0
    vertexNum = 0

    def __init__(self):
        self.vbo = gl.glGenBuffers(1)

    # def __del__(self):
    #     gl.glDeleteBuffers(1, self.vbo)

    def bind(self):
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)

    def setBuffer(self, bufferDataArray: np.ndarray, vertexAttribSize: int):
        """
        :param vertexAttribSize: the size of the vertex attribute
        :type vertexAttribSize: int
        :param bufferDataArray: the vertices data. It will be flatten in row-major order if its dimension isn't one
        :type bufferDataArray: numpy.ndarray
        """
        # type conversion
        if bufferDataArray.dtype != np.dtype("float32"):
            bufferDataArray = bufferDataArray.astype(np.dtype("float32"))
        bufferData = bufferDataArray.flatten("C")  # flatten in row-major order
        self.vertexAttribSize = vertexAttribSize

        bufferSize = bufferDataArray.size
        self.vertexNum = bufferSize // vertexAttribSize  # for safety reason, take floor division to get int result
        byteLength = 4 * bufferSize  # 4 is the size of float32

        self.bind()
        gl.glBufferData(gl.GL_ARRAY_BUFFER, byteLength, bufferData, gl.GL_STATIC_DRAW)

    def setAttribPointer(self, attribLoc, stride=0, offset=0, attribSize=0):
        attribSize = self.vertexAttribSize if attribSize == 0 else attribSize
        if attribSize == 0:
            raise Exception("Cannot set vertex attrib with empty attribSize")

        # If the attribLoc is not available, return and do nothing
        if attribLoc < 0:
            print("Warning: Cannot set attrib pointer at ", attribLoc)
            return

        # set vertex pointer
        self.bind()
        offset = ctypes.c_void_p(offset * 4)
        stride *= 4
        gl.glVertexAttribPointer(attribLoc, attribSize, gl.GL_FLOAT, gl.GL_FALSE, stride, offset)
        gl.glEnableVertexAttribArray(attribLoc)

    def draw(self):
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.vertexNum)


class EBO:
    """
    A class to handle EBO in OpenGL, with some help functions
    """
    ebo = None
    indexNum = 0
    triangleNum = 0

    def __init__(self):
        self.ebo = gl.glGenBuffers(1)

    # def __del__(self):
    #     gl.glDeleteBuffers(1, self.ebo)

    def bind(self):
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ebo)

    def setBuffer(self, bufferDataArray: np.ndarray):
        if bufferDataArray.dtype != np.dtype("int32"):
            bufferDataArray = bufferDataArray.astype(np.dtype("int32"))
        bufferData = bufferDataArray.flatten("C")  # row-major order flatten

        self.indexNum = bufferData.size
        self.triangleNum = self.indexNum // 3  # floor division to get triangle number
        byteLength = 4 * self.indexNum

        self.bind()
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, byteLength, bufferData, gl.GL_STATIC_DRAW)

    def draw(self):
        gl.glDrawElements(gl.GL_TRIANGLES, self.indexNum, gl.GL_UNSIGNED_INT, None)


class VAO:
    """
    Responsible for VAO
    """
    vao = None

    def __init__(self):
        self.vao = gl.glGenVertexArrays(1)

    # def __del__(self):
    #     gl.glDeleteVertexArrays(1, self.vao)

    def bind(self):
        gl.glBindVertexArray(self.vao)

    def unbind(self):
        gl.glBindVertexArray(0)


# A global variable in this scope to store next texture id, there should be no duplicate textureUnitID
NextTextureID = 1

class Texture:
    """
    Packed help functions to deal with texture mapping in OpenGL, can be used to store multiple textures
    """
    textureName = 0
    textureUnitID = 0

    def __init__(self):
        global NextTextureID

        # assign a texture image unit for this sampler
        self.textureUnitID = NextTextureID
        NextTextureID = NextTextureID % 16 + 1

    def setTextureImage(self, image):
        self.textureName = gl.glGenTextures(1)

        # flip image upside down.
        # trim to RGB channels, even if a channel provided
        image = image[::-1, :, 0:3]
        image = image.astype(np.dtype("uint8"))

        height, width, channel = image.shape
        imageData = image.flatten("C")

        gl.glBindTexture(gl.GL_TEXTURE_2D, self.textureName)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, width, height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, imageData)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
        self.setTextureParameters()

    def setTextureParameters(self):
        # for 2D texture, need wrap along s and t
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    def bind(self, glslVariableLoc):
        gl.glActiveTexture(gl.GL_TEXTURE0 + self.textureUnitID)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.textureName)
        gl.glUniform1i(glslVariableLoc, self.textureUnitID)

    def unbind(self, glslVariableLoc):
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        gl.glUniform1i(glslVariableLoc, 0)

