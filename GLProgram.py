"""
OpenGL shader program used as part of rendering pipeline.
Model & color transformations are applied here. 

Author: Zezhou Sun
Modified by Daniel Scrivener 07/2022
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
import math


def perspectiveMatrix(angleOfView, near, far):
    result = np.identity(4)
    angleOfView = min(179, max(0, angleOfView))
    scale = 1 / math.tan(0.5 * angleOfView * math.pi / 180)
    fsn = far - near
    result[0, 0] = scale
    result[1, 1] = scale
    result[2, 2] = - far / fsn
    result[3, 2] = - far * near / fsn
    result[2, 3] = -1
    result[3, 3] = 0


class GLProgram:
    program = None

    vertexShaderSource = None
    fragmentShaderSource = None
    attribs = None

    vs = None  # vertex shader
    fs = None  # Fragment shader

    ready = False  # a control flag which reflect if this GLprogram is ready
    debug = 0

    def __init__(self) -> None:
        self.program = gl.glCreateProgram()

        self.ready = False

        # define attribs name and corresponding method to set it
        self.attribs = {
            "vertexPos": "aPos",
            "vertexNormal": "aNormal",
            "vertexColor": "aColor",
            "vertexTexture": "aTexture",

            "textureImage": "theTexture01",

            "projectionMat": "projection",
            "viewMat": "view",
            "modelMat": "model",

            "vertexJoints": "joint",
            "vertexJointWeights" : "jw",

            "currentColor": "cColor"
        }

        self.vertexShaderSource = self.genVertexShaderSource()
        self.fragmentShaderSource = self.genFragShaderSource()

    def __del__(self) -> None:
        try:
            gl.glDeleteProgram(self.program)
        except Exception as e:
            pass

    @staticmethod
    def load_shader(src: str, shader_type: int) -> int:
        shader = gl.glCreateShader(shader_type)
        gl.glShaderSource(shader, src)
        gl.glCompileShader(shader)
        error = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
        if error != gl.GL_TRUE:
            info = gl.glGetShaderInfoLog(shader)
            gl.glDeleteShader(shader)
            raise Exception(info)
        return shader

    def genVertexShaderSource(self):
        vss = f'''
        #version 330 core
        in vec3 {self.attribs["vertexPos"]};
        in vec3 {self.attribs["vertexNormal"]};
        in vec3 {self.attribs["vertexColor"]};
        in vec2 {self.attribs["vertexTexture"]};
        
        out vec3 vPos;
        out vec3 vColor;
        smooth out vec3 vNormal;
        out vec2 vTexture;
        
        uniform mat4 {self.attribs["projectionMat"]};
        uniform mat4 {self.attribs["viewMat"]};
        uniform mat4 {self.attribs["modelMat"]};
        
        void main()
        {{
            gl_Position = {self.attribs["projectionMat"]} * {self.attribs["viewMat"]} * {self.attribs["modelMat"]} * vec4({self.attribs["vertexPos"]}, 1.0);
            vPos = vec3({self.attribs["modelMat"]} * vec4({self.attribs["vertexPos"]}, 1.0));
            vColor = {self.attribs["vertexColor"]};
            vNormal = normalize(transpose(inverse({self.attribs["modelMat"]})) * vec4({self.attribs["vertexNormal"]}, 0.0) ).xyz;
            vTexture = {self.attribs["vertexTexture"]};
        }}
        '''
        return vss

    def genFragShaderSource(self):
        fss = f"""
        #version 330 core
        
        in vec3 vPos;
        in vec3 vColor;
        smooth in vec3 vNormal;
        in vec2 vTexture;

        uniform vec3 {self.attribs["currentColor"]};
        uniform sampler2D {self.attribs["textureImage"]};
        
        out vec4 FragColor;
        void main()
        {{
            // These three lines prevent glsl from optimizing out attributes (vPos, vColor, etc.).
            // They are otherwise meaningless.
            vec4 placeHolder = vec4(vPos+vColor+vNormal+vec3(vTexture, 1), 0);
            FragColor = -1 * abs(placeHolder);
            FragColor = clamp(FragColor, 0, 1);

            // Shade according to vertex colors
            FragColor = vec4({self.attribs["currentColor"]}, 1.0);
        }}
        """
        return fss

    def set_vss(self, vss: str):
        if not isinstance(vss, str):
            raise TypeError("Vertex shader source code must be a string")
        self.vertexShaderSource = vss

    def set_fss(self, fss):
        if not isinstance(fss, str):
            raise TypeError("Fragment shader source code must be a string")
        self.fragmentShaderSource = fss

    def getAttribLocation(self, name):
        programName = self.getAttribName(name)
        attribLoc = gl.glGetAttribLocation(self.program, programName)
        if attribLoc == -1 and self.debug > 1:
            print(f"Warning: Attrib {name} cannot found. Might have been optimized off")
        return attribLoc

    def getUniformLocation(self, name, lookThroughAttribs=True):
        if lookThroughAttribs:
            variableName = self.getAttribName(name)
        else:
            variableName = name
        uniformLoc = gl.glGetUniformLocation(self.program, variableName)
        if uniformLoc == -1 and self.debug > 1:
            print(f"Warning: Uniform {name} cannot found. Might have been optimized off")
        return uniformLoc

    def getAttribName(self, attribIndexName):
        return self.attribs[attribIndexName]

    def compile(self, vs_src=None, fs_src=None) -> None:
        if vs_src:
            self.set_vss(vs_src)
        else:
            vs_src = self.vertexShaderSource

        if fs_src:
            self.set_fss(fs_src)
        else:
            fs_src = self.fragmentShaderSource

        if not (vs_src and fs_src):
            raise Exception("shader source code missing")

        vs = self.load_shader(vs_src, gl.GL_VERTEX_SHADER)
        if not vs:
            return
        fs = self.load_shader(fs_src, gl.GL_FRAGMENT_SHADER)
        if not fs:
            return
        gl.glAttachShader(self.program, vs)
        gl.glAttachShader(self.program, fs)
        gl.glLinkProgram(self.program)
        error = gl.glGetProgramiv(self.program, gl.GL_LINK_STATUS)
        if error != gl.GL_TRUE:
            info = gl.glGetShaderInfoLog(self.program)
            raise Exception(info)

        self.ready = True

    def use(self):
        """
        This is required before the uniforms set up.
        """
        if not self.ready:
            raise Exception("GLProgram must compile before use it")
        gl.glUseProgram(self.program)

    # some help methods to set uniform in program
    def setMat4(self, name, mat, lookThroughAttribs=True):
        self.use()
        if mat.shape != (4, 4):
            raise Exception("Projection Matrix must have 4x4 shape")
        gl.glUniformMatrix4fv(self.getUniformLocation(name, lookThroughAttribs), 1, gl.GL_FALSE, mat.flatten("C"))

    def setMat3(self, name, mat, lookThroughAttribs=True):
        self.use()
        if mat.shape != (3, 3):
            raise Exception("Projection Matrix must have 3x3 shape")
        gl.glUniformMatrix3fv(self.getUniformLocation(name, lookThroughAttribs), 1, gl.GL_FALSE, mat.flatten("C"))

    def setMat2(self, name, mat, lookThroughAttribs=True):
        self.use()
        if mat.shape != (2, 2):
            raise Exception("Projection Matrix must have 2x2 shape")
        gl.glUniformMatrix2fv(self.getUniformLocation(name, lookThroughAttribs), 1, gl.GL_FALSE, mat.flatten("C"))

    def setVec4(self, name, vec, lookThroughAttribs=True):
        self.use()
        if vec.size != 4:
            raise Exception("Vector must have size 4")
        gl.glUniform4fv(self.getUniformLocation(name, lookThroughAttribs), 1, vec)

    def setVec3(self, name, vec, lookThroughAttribs=True):
        self.use()
        if vec.size != 3:
            raise Exception("Vector must have size 3")
        gl.glUniform3fv(self.getUniformLocation(name, lookThroughAttribs), 1, vec)

    def setVec2(self, name, vec, lookThroughAttribs=True):
        self.use()
        if vec.size != 2:
            raise Exception("Vector must have size 2")
        gl.glUniform2fv(self.getUniformLocation(name, lookThroughAttribs), 1, vec)

    def setBool(self, name, value, lookThroughAttribs=True):
        self.use()
        if value not in (0, 1):
            raise Exception("bool only accept True/False/0/1")
        gl.glUniform1i(self.getUniformLocation(name, lookThroughAttribs), int(value))

    def setInt(self, name, value, lookThroughAttribs=True):
        self.use()
        if value != int(value):
            raise Exception("set int only accept  integer")
        gl.glUniform1i(self.getUniformLocation(name, lookThroughAttribs), int(value))

    def setFloat(self, name, value, lookThroughAttribs=True):
        self.use()
        gl.glUniform1f(self.getUniformLocation(name, lookThroughAttribs), float(value))
