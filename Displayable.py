"""
Define an abstract class Displayable here.
First version in 09/26/2018

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""


class Displayable:
    """
    Interface for displayable object
    """
    def __init__(self):
        pass

    def draw(self):
        raise NotImplementedError

    def initialize(self):
        raise NotImplementedError
