"""
Set up our display pipeline. WxPython is used to solve system compatibility problems. It is mainly focusing on
creating a display window with a canvas. We will let OpenGL draw on it. All these things have been wrapped up,
and the main class should inherit this class. First version Created on 09/27/2018

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""

from Component import Component

try:
    import wx
    from wx import glcanvas
except ImportError:
    raise ImportError("Required dependency wxPython not present")

try:
    import OpenGL

    try:
        import OpenGL.GL as gl
        import OpenGL.GLU as glu
    except ImportError:
        print("Patching for Big Sur")
        from ctypes import util

        orig_util_find_library = util.find_library

        def new_util_find_library(name):
            res = orig_util_find_library(name)
            if res:
                return res
            return "/System/Library/Frameworks/" + name + ".framework/" + name

        util.find_library = new_util_find_library
        import OpenGL.GL as gl
        import OpenGL.GLU as glu
except ImportError:
    raise ImportError("Required dependency PyOpenGL not present")

import math
import random
import numpy as np

from Point import Point
from ColorType import ColorType
from Quaternion import Quaternion

############################### System Checking ################################

WX_MINIMUM_REQUIRED = "3.0.0"
OPENGL_MINIMUM_REQUIRED = "3.1.0"

# Package version checking
if wx.__version__ < WX_MINIMUM_REQUIRED:
    # Not fully tested yet. But version 3.0.0+ should work based on changelog
    raise ImportError("wxPython minimum required " + WX_MINIMUM_REQUIRED)
if OpenGL.__version__ < OPENGL_MINIMUM_REQUIRED:
    # Not fully tested yet.
    raise ImportError("PyOpenGL minimum required " + OPENGL_MINIMUM_REQUIRED)


############################ End of System Checking #############################


class CanvasBase(glcanvas.GLCanvas):
    """
    All functions work on interruptions and events start with capital letter
    functions for public use start with lower case letter
    functions for local use (accessible from outside) start with _(single underscore)
    functions for private use (not accessible outside) start with __ (double underscore)
    """

    size = None
    context = None
    stateChanged = False
    topLevelComponent = None
    init = False
    viewing_quaternion = None
    dragging_event = False
    new_dragging_event = False

    fps = 120  # frame per second, -1 to disable auto refresh

    def __init__(self, parent):
        """
        Inherit from WxPython GLCanvas class. Bind implemented methods to window events.

        :param parent: The WxPython frame you want to inherit from
        :type parent: wx.Frame
        """
        # Initialize parent class
        attrib = glcanvas.GLAttributes()
        # Defaults() is required. Otherwise MacOS will get blank screen,
        # For the depth size, macOS support <= 24, Windows support 16-32, Linux requires >= 24
        attrib.Defaults().Depth(24).EndList()
        super(CanvasBase, self).__init__(parent, attrib)
        # Initialize public variables
        self.stateChanged = False
        self.init = False
        self.size = (0, 0)
        self.topLevelComponent = Component(Point((0, 0, 0)))
        self.viewing_quaternion = Quaternion()
        self.timer = wx.Timer(self, 1)  # TIMER_ID set to 1
        # Bind event to functions
        # self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeft)
        self.Bind(wx.EVT_RIGHT_UP, self.OnMouseRight)
        self.Bind(wx.EVT_CHAR, self.OnKeyDown)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnScroll)
        # refresh canvas with constant frame rate
        self.Bind(wx.EVT_TIMER, self.OnPaint)

        if self.fps > 0:
            self.timer.Start(int(1000 / self.fps), oneShot=wx.TIMER_CONTINUOUS)

    def OnScroll(self, event):
        """
        Bind method to mouse wheel rotation

        :param event: mouse event
        :return: None
        """
        self.Interrupt_Scroll(event.GetWheelRotation())
        self.Refresh(True)

    def OnTimer(self, event):
        self.OnPaint(event)

    def OnResize(self, event):
        """
        Called when resize of window happen, this will run before OnPaint in first running

        :param event: Canvas resize event
        :return: None
        """
        self.context = glcanvas.GLContext(self)
        self.size = self.GetClientSize()
        self.size[1] = max(1, self.size[1])  # avoid divided by 0
        self.SetCurrent(self.context)

        # Update screen and display
        self.init = False
        self.Refresh(eraseBackground=True)
        self.Update()

    def OnIdle(self, event):
        pass

    def OnPaint(self, event=None):
        """
        Bind to wxPython paint event, this will be called in every frame drawing.
        This method will also control the environment initialization and model update
        with control flag self.init and self.stateChanged

        :param event: wxpython paint event
        :return: None
        """
        self.SetCurrent(self.context)
        if not self.init:
            # Init the OpenGL environment if not initialized
            self.InitGL()
            self.init = True
        if self.stateChanged:
            # If there is any changes in model, we need to update the model from the very beginning
            self.ModelChanged()
            self.stateChanged = False
        # the draw method
        self.OnDraw()

    def OnDraw(self):
        """
        Wrap OpenGL commands, to draw on canvas
        :return: None
        """
        self.SetCurrent(self.context)
        # clear color buffer and depth buffer
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # Swap Buffer to display canvas
        self.SwapBuffers()

    def ModelChanged(self):
        """
        Reinitialize model start from the top level if model value changed
        """
        self.topLevelComponent.initialize()
        self.topLevelComponent.update()

    def InitGL(self):
        """
        Initialize the OpenGL environment. Set up lighting and rendering settings
        Call this method when canvas property changed. This will reset lighting
        """
        self.SetCurrent(self.context)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        self.size = self.GetClientSize()

        # Initialize all components and draw them
        self.topLevelComponent.initialize()
        self.topLevelComponent.update()

        # Set up display environment
        gl.glPolygonMode(gl.GL_FRONT, gl.GL_FILL)
        gl.glEnable(gl.GL_COLOR_MATERIAL)
        gl.glColorMaterial(gl.GL_FRONT, gl.GL_AMBIENT_AND_DIFFUSE)

        # only draw front-facing faces
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glCullFace(gl.GL_BACK)

        # clear background on canvas.
        gl.glClearColor(0, 0, 0, 0)
        gl.glShadeModel(gl.GL_SMOOTH)

        # Set up light source
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, [0, 0, 5, 0], 0)
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_AMBIENT, [0.25, 0.25, 0.25, 1], 0)
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, [1, 1, 1, 1], 0)
        gl.glLightfv(gl.GL_LIGHT1, gl.GL_POSITION, [0, 5, 0, 0], 0)
        gl.glLightfv(gl.GL_LIGHT1, gl.GL_AMBIENT, [0.25, 0.25, 0.25, 1], 0)
        gl.glLightfv(gl.GL_LIGHT1, gl.GL_DIFFUSE, [1, 1, 1, 1], 0)
        gl.glLightfv(gl.GL_LIGHT2, gl.GL_POSITION, [5, 0, 0, 0], 0)
        gl.glLightfv(gl.GL_LIGHT2, gl.GL_AMBIENT, [0.25, 0.25, 0.25, 1], 0)
        gl.glLightfv(gl.GL_LIGHT2, gl.GL_DIFFUSE, [1, 1, 1, 1], 0)
        gl.glEnable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_LIGHT0)
        gl.glEnable(gl.GL_LIGHT1)
        gl.glEnable(gl.GL_LIGHT2)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_NORMALIZE)

        # this is for depth buffer debug purpose only
        # print({
        #     "GL_DEPTH_BIAS": gl.glGetIntegerv(gl.GL_DEPTH_BIAS),
        #     "GL_DEPTH_BITS": gl.glGetIntegerv(gl.GL_DEPTH_BITS),
        #     "GL_DEPTH_CLEAR_VALUE": gl.glGetIntegerv(gl.GL_DEPTH_CLEAR_VALUE),
        #     "GL_DEPTH_FUNC is GL_LESS": gl.glGetIntegerv(gl.GL_DEPTH_FUNC),
        #     "GL_DEPTH_RANGE": gl.glGetIntegerv(gl.GL_DEPTH_RANGE),
        #     "GL_DEPTH_SCALE": gl.glGetIntegerv(gl.GL_DEPTH_SCALE),
        #     "GL_DEPTH_TEST": gl.glGetIntegerv(gl.GL_DEPTH_TEST),
        #     "GL_DEPTH_WRITEMASK": gl.glGetIntegerv(gl.GL_DEPTH_WRITEMASK)
        # })

    def OnDestroy(self, event):
        """
        Window destroy event binding

        :param event: Window destroy event
        :return: None
        """
        print("Destroy Window")

    def OnMouseMotion(self, event):
        """
        Mouse motion interrupt bindings

        :param event: mouse motion event
        :return: None
        """
        if event.LeftIsDown():
            # If this is a dragging event with left button down
            self.new_dragging_event = not self.dragging_event
            self.dragging_event = True
            self.Interrupt_MouseLeftDragging(event.GetX(), self.size[1] - event.GetY())
            self.Refresh(True)
        elif event.RightIsDown():
            # If this is a dragging event with right button down
            self.new_dragging_event = not self.dragging_event
            self.dragging_event = True
            self.Interrupt_MouseMiddleDragging(
                event.GetX(), self.size[1] - event.GetY()
            )  # use middle method
            self.Refresh(True)
        elif event.MiddleIsDown():
            self.new_dragging_event = not self.dragging_event
            self.dragging_event = True
            self.Interrupt_MouseMiddleDragging(
                event.GetX(), self.size[1] - event.GetY()
            )
            self.Refresh(True)
        else:
            # Normal Mouse Moving
            self.dragging_event = False
            self.Interrupt_MouseMoving(event.GetX(), self.size[1] - event.GetY())
            self.Refresh(True)

    # Definition for interface
    def OnMouseLeft(self, event):
        """
        Mouse left click event binding

        :param event: left mouse click event
        :return: None
        """
        x = event.GetX()
        y = event.GetY()
        self.Interrupt_MouseL(x, self.size[1] - y)
        self.Refresh(True)

    def OnMouseRight(self, event):
        """
        Mouse right click event binding

        :param event: right mouse click event
        :return: None
        """
        x = event.GetX()
        y = event.GetY()
        self.Interrupt_MouseR(x, self.size[1] - y)
        self.Refresh(True)

    def OnKeyDown(self, event):
        """
        keyboard press event binding

        :param event: keyboard press event
        :return: None
        """
        keycode = event.GetKeyCode()
        self.Interrupt_Keyboard(keycode)
        self.Refresh(True)

    def modelUpdate(self):
        """
        Call this method once model changed, update model on canvas

        :return: None
        """
        self.stateChanged = True
        self.Refresh(True)

    def Interrupt_Scroll(self, wheelRotation):
        pass

    def Interrupt_MouseL(self, x, y):
        pass  # Fully Override please

    def Interrupt_MouseR(self, x, y):
        pass  # Fully Override please

    def Interrupt_Keyboard(self, keycode):
        pass  # Fully Override please

    def Interrupt_MouseLeftDragging(self, x, y):
        pass  # Fully Override please

    def Interrupt_MouseRightDragging(self, x, y):
        pass  # Fully Override please

    def Interrupt_MouseMiddleDragging(self, x, y):
        pass  # Fully Override please

    def Interrupt_MouseMoving(self, x, y):
        pass  # Fully Override please


if __name__ == "__main__":
    app = wx.App(False)
    # Set FULL_REPAINT_ON_RESIZE will repaint everything when scaling the frame, here is the style setting for it: wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE
    # Resize disabled in this one
    frame = wx.Frame(
        None,
        size=(500, 500),
        title="Test",
        style=wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE,
    )
    canvas = CanvasBase(frame)

    frame.Show()
    app.MainLoop()
