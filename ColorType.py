"""
This file contains a basic ColorType class, which is used to store RGB color in float.
For performance reasons, instances of this class will only have three variable slots: r, g and b.
r, g and b will be stored as floats in range [0, 1].
We prepared several methods to import and export different RGB formats.
First version Created on 09/23/2018

Performance Suggestions:

* If you need to access the r, g and b values, direct RGB access is faster than access by method


:author: micou(Zezhou Sun)
:version: 2021.2.1
"""


class ColorType:
    """
    A class to manage RGB color
    """
    __slots__ = ["r", "g", "b"]

    # r, g, b are floats in [0, 1]

    def __init__(self, red: float = 0, green: float = 0, blue: float = 0) -> None:
        """
        can use r,g,b to create a ColorType
        recommend to pass through arguments using specific keys and values

        :param red: Red color value, should be in range [0, 1]
        :param green: Green color value, should be in range [0, 1]
        :param blue: Blue color value, should be in range [0, 1]
        :type red: float
        :type green: float
        :type blue: float
        :rtype: None
        """
        self.setRGB(red, green, blue)

    def __iter__(self):
        return iter((self.r, self.g, self.b))

    def __getitem__(self, i):
        if i == 0:
            return self.r
        if i == 1:
            return self.g
        if i == 2:
            return self.b
        raise Exception("Out of bound")

    def __setitem__(self, key, value):
        if key == 0:
            self.r = value
        if key == 1:
            self.g = value
        if key == 2:
            self.b = value

    def __repr__(self):
        """
        Defines ColorType print string
        """
        return str(self.getRGB())

    def __hash__(self):
        """
        Defines ColorType hashing. This will be needed in Set and Dict.
        """
        return hash((self.r, self.g, self.b))

    def __eq__(self, other):
        """
        For ColorType comparison
        """
        try:
            result = self.r == other.r and \
                     self.g == other.g and \
                     self.b == other.b
        except AttributeError:
            return False
        return result

    def setRGB(self, r=0, g=0, b=0):
        """
        This method will check v values to make sure they are in range.
        This is safe for v value, but might affect the ColorType performance.

        :param r: Red color value, should be in range [0, 1]
        :param g: Green color value, should be in range [0, 1]
        :param b: Blue color value, should be in range [0, 1]
        :type r: float
        :type g: float
        :type b: float
        :rtype: None
        """
        self.r = min(1.0, max(0.0, r))
        self.g = min(1.0, max(0.0, g))
        self.b = min(1.0, max(0.0, b))

    def setRGB_8bit(self, r=0, g=0, b=0):
        """
        :param r: Red color value, should be in range [0, 255]
        :param g: Green color value, should be in range [0, 255]
        :param b: Blue color value, should be in range [0, 255]
        :type r: int
        :type g: int
        :type b: int
        :rtype: None
        """
        self.r = r / 255
        self.g = g / 255
        self.b = b / 255

    def setRGB_ARGB(self, argb):
        """
        set RGB by using only one integer, which is in ARGB format

        :param argb: ARGB color in int. Int length is 32 bits, the highest 8 bits are transparent value (\
        discarded), and it is followed by 8 bits red, 8 bits green and 8 bits blue.
        :type argb: int
        :rtype: None
        """
        self.r = ((argb & 0x00ff0000) >> 16) / 255
        self.g = ((argb & 0x0000ff00) >> 8) / 255
        self.b = (argb & 0x000000ff) / 255

    def setRGB_RGBA(self, rgba):
        """
        set RGB by using only one integer, which is in RGBA format

        :param rgba: ARGB color in int. Int length is 32 bits, the highest 8 bits are red value,\
        and 8 bits green and 8 bits blue.
        :type rgba: int
        :rtype: None
        """
        self.r = ((rgba >> 24) & 0xff) / 255.0
        self.g = ((rgba >> 16) & 0xff) / 255.0
        self.b = ((rgba >> 8) & 0xff) / 255.0

    def getRGB(self):
        """
        Get current RGB values as a tuple.

        :rtype: tuple[float]
        """
        return self.r, self.g, self.b

    def getRGB_8bit(self):
        """
        Get a tuple which contains current RGB 8 bits values.
        Each color is represented in char format (8 bits integer, value in range [0, 255])

        :rtype: tuple[int]
        """
        return int(self.r * 255), int(self.g * 255), int(self.b * 255)

    def getRGB_RGBA(self):
        """
        Get color in RGBA format

        :rtype: int
        """
        RGB_tuple = self.getRGB_8bit()
        return (RGB_tuple[0] << 24) | (RGB_tuple[1] << 16) | (RGB_tuple[2] << 8) | 0xff

    def getRGB_BGR(self):
        """
        Get color in BGR format. This format is popularly used in the OpenCV library.

        :rtype: int
        """
        RGB_tuple = self.getRGB_8bit()
        return (RGB_tuple[2] << 16) | RGB_tuple[1] << 8 | RGB_tuple[0]

    def copy(self):
        """
        A deep copy of current ColorType instance.

        :rtype: ColorType
        """
        return ColorType(self.r, self.g, self.b)


YELLOW = ColorType(1, 1, 0)
ORANGE = ColorType(1, 0.5, 0)
DARKORANGE1 = ColorType(1, 140 / 255, 0)
DARKORANGE2 = ColorType(200 / 255, 95 / 255, 0)
DARKORANGE3 = ColorType(160 / 255, 80 / 255, 0)
DARKORANGE4 = ColorType(130 / 255, 60 / 255, 0)

DARKGREEN = ColorType(0, 100 / 255, 0)
GREEN = ColorType(0, 1, 0)
SOFTGREEN = ColorType(192/255, 238/255, 0)
GREENYELLOW = ColorType(173 / 255, 255 / 255, 47 / 255)
LIGHTGREEN = ColorType(144 / 255, 238 / 255, 144 / 255)
SEAGREEN = ColorType(32 / 255, 178 / 255, 170 / 255)
BLUEGREEN = ColorType(3/255, 106/255, 110/255)

RED = ColorType(1, 0, 0)
SOFTRED = ColorType(255/255, 127/255,  154/255)
PURPLE = ColorType(0.5, 0, 0.5)
PINK = ColorType(1, 192 / 255, 203 / 255)

NAVY = ColorType(0, 0, 0.5)
BLUE = ColorType(0, 0, 1)
SOFTBLUE = ColorType(115/255, 197/255, 255/255)
CYAN = ColorType(0, 1, 1)
DODGERBLUE = ColorType(30 / 255, 144 / 255, 255 / 255)
DEEPSKYBLUE = ColorType(0, 191 / 255, 255 / 255)

SILVER = ColorType(0.75, 0.75, 0.75)
WHITE = ColorType(1.0, 1.0, 1.0)
GRAY = ColorType(0.2, 0.2, 0.2)
BLACK = ColorType(0.0, 0.0, 0.0)

if __name__ == "__main__":
    c = ColorType(0.5, 0.2, 0.1)
    print(c.getRGB_8bit())
    print(c.getRGB_RGBA())
    print(c)
    print()
    c = ColorType()
    c.setRGB_ARGB(8401690)
    print(c.getRGB_8bit())
    print(c.getRGB_RGBA())
    print(c)
    print()
    b = ColorType(*c.getRGB())
    print(b)

    # Test for set
    cs = set()
    cs.add(ColorType(1, 0, 1))
    cs.add(ColorType(1, 0, -1))
    cs.add(ColorType(0.5, 1, 1))
    cs.add(ColorType(1, 0, 1))
    print(cs)
