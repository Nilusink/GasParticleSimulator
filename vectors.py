"""
vectors.py
26. May 2024

defines game Vectors (copied from nilusink/amoginarium)

Author:
Nilusink
"""
import typing as tp
import math as m


class Vec2[T: (int, float)]:
    x: T
    y: T
    angle: T
    length: T

    def __init__(self) -> None:
        self.__x: T = 0
        self.__y: T = 0
        self.__angle: T = 0
        self.__length: T = 0

    # variable getters / setters
    @property
    def x(self) -> T:
        return self.__x

    @x.setter
    def x(self, value: T):
        self.__x = value
        self.__update("c")

    @property
    def y(self) -> T:
        return self.__y

    @y.setter
    def y(self, value: T):
        self.__y = value
        self.__update("c")

    @property
    def xy(self) -> tuple[T, T]:
        return self.__x, self.__y

    @xy.setter
    def xy(self, xy: tuple[T, T]):
        self.__x = xy[0]
        self.__y = xy[1]
        self.__update("c")

    @property
    def angle(self) -> float:
        """
        value in radian
        """
        return self.__angle

    @angle.setter
    def angle(self, value: float):
        """
        value in radian
        """
        value = self.normalize_angle(value)

        self.__angle = value
        self.__update("p")

    @property
    def length(self) -> float:
        return self.__length

    @length.setter
    def length(self, value: float):
        self.__length = value
        self.__update("p")

    @property
    def polar(self) -> tuple[float, float]:
        return self.__angle, self.__length

    @polar.setter
    def polar(self, polar: tuple[float, float]):
        self.__angle = polar[0]
        self.__length = polar[1]
        self.__update("p")

    # interaction
    def split_vector(self, direction: tp.Self) -> tuple[tp.Self, tp.Self]:
        """
        :param direction: A vector facing in the wanted direction
        :return: tuple[Vector in only that direction, everything else]
        """
        a = (direction.angle - self.angle)
        facing = Vec2.from_polar(
            angle=direction.angle,
            length=self.length * m.cos(a)
        )
        other = Vec2.from_polar(
            angle=direction.angle - m.pi / 2,
            length=self.length * m.sin(a)
        )

        return facing, other

    def copy(self) -> tp.Self:
        return Vec2().from_cartesian(x=self.x, y=self.y)

    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "angle": self.angle,
            "length": self.length,
        }

    def normalize(self) -> tp.Self:
        """
        set a vectors length to 1
        """
        self.length = 1
        return self

    def mirror(self, mirror_by: tp.Self) -> tp.Self:
        """
        mirror a vector by another vector
        """
        mirror_by = mirror_by.copy().normalize()
        ang_d = mirror_by.angle - self.angle
        self.angle = mirror_by.angle + 2 * ang_d
        return self

    # maths
    def __add__(self, other: tp.Self | T) -> tp.Self:
        if issubclass(type(other), Vec2):
            return Vec2.from_cartesian(x=self.x + other.x, y=self.y + other.y)

        return Vec2.from_cartesian(x=self.x + other, y=self.y + other)

    def __sub__(self, other: tp.Self | T) -> tp.Self:
        if issubclass(type(other), Vec2):
            return Vec2.from_cartesian(x=self.x - other.x, y=self.y - other.y)

        return Vec2.from_cartesian(x=self.x - other, y=self.y - other)

    def __mul__(self, other: tp.Self | float):
        if issubclass(type(other), Vec2):
            return Vec2.from_polar(
                angle=self.angle + other.angle,
                length=self.length * other.length
            )

        return Vec2.from_cartesian(x=self.x * other, y=self.y * other)

    def __truediv__(self, other: tp.Self):
        return Vec2.from_cartesian(x=self.x / other, y=self.y / other)

    # internal functions
    def __update(
            self,
            calc_from: tp.Literal["p", "polar", "c", "cartesian"]
    ) -> None:
        """
        :param calc_from: polar (p) | cartesian (c)
        """
        if calc_from in ("p", "polar"):
            self.__x = m.cos(self.angle) * self.length
            self.__y = m.sin(self.angle) * self.length

        elif calc_from in ("c", "cartesian"):
            self.__length = m.sqrt(self.x**2 + self.y**2)
            self.__angle = m.atan2(self.y, self.x)

        else:
            raise ValueError("Invalid value for \"calc_from\"")

    def __abs__(self) -> float:
        return m.sqrt(self.x**2 + self.y**2)

    def __repr__(self):
        return f"<\n" \
               f"\tVec2:\n" \
               f"\tx:{self.x}\ty:{self.y}\n" \
               f"\tangle:{self.angle}\tlength:{self.length}\n" \
               f">"

    # static and class methods.
    # creation of new instances
    @classmethod
    def from_cartesian(cls, x: T, y: T) -> tp.Self:
        p = cls()
        p.xy = x, y

        return p

    @classmethod
    def from_polar(cls, angle: float, length: float) -> tp.Self:
        p = cls()
        p.polar = angle, length

        return p

    @classmethod
    def from_dict(cls, dictionary: dict) -> tp.Self:
        if "x" in dictionary and "y" in dictionary:
            return cls.from_cartesian(x=dictionary["x"], y=dictionary["y"])

        elif "angle" in dictionary and "length" in dictionary:
            return cls.from_polar(
                angle=dictionary["angle"],
                length=dictionary["length"]
                )

        else:
            raise KeyError(
                "either (x & y) or (angle & length) must be in dict!"
            )

    @staticmethod
    def normalize_angle(value: float) -> float:
        while value > 2 * m.pi:
            value -= 2 * m.pi

        while value < 0:
            value += 2 * m.pi

        return value
