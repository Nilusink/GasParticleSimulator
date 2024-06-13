"""
box.py
1. June 2024

Thermodynamics for the simulator

Author:
Nilusink
"""
from physics_calculations import volume_from_pressure
from vectors import Vec2
import pygame


class _Box:
    def __init__(self) -> None:
        self._pos = Vec2.from_cartesian(100, 100)
        self._size = Vec2.from_cartesian(600, 600)
        self._max_width = 1000
        self._min_width = 100
        self._world_size = ...

    @property
    def pos(self) -> Vec2:
        return self._pos.copy()

    @property
    def size(self) -> Vec2:
        return self._size.copy()

    def set_length(self, value: float) -> None:
        # only resize if in bounds
        if self._min_width > value:
            self._size.x = self._min_width

        elif value > self._max_width:
            self._size.x = self._max_width

        else:
            self._size.x = value

    @property
    def left(self) -> int:
        return int(self._pos.x)

    @property
    def right(self) -> int:
        return int(self._pos.x + self.size.x)

    @property
    def top(self) -> int:
        return int(self._pos.y)

    @property
    def bottom(self) -> int:
        return int(self._pos.y + self.size.y)

    @property
    def world_width(self) -> int:
        return self._world_size[0]

    @property
    def world_height(self) -> int:
        return self._world_size[1]

    @property
    def world_size(self) -> tuple[int, int]:
        return self._world_size.copy()

    @world_size.setter
    def world_size(self, value: tuple[int, int]) -> None:
        if self._world_size is not ...:
            raise ValueError("World size already set")

        self._world_size = value

    @property
    def volume(self) -> float:
        return (self._size.x * self._size.y) * 1e-28

    def draw(self, screen) -> None:
        pygame.draw.rect(
            screen,
            (0, 0, 0, 255),
            pygame.rect.Rect(self.pos.xy, self.size.xy),
            3
        )

    def recalculate_from_pressure(
            self,
            pressure: float,
            particles: list
    ) -> None:
        """
        recalculate the size using pressure
        """
        new_volume = volume_from_pressure(particles, pressure) * 1e28
        new_width = new_volume / self._size.y

        # only resize if in bounds
        if self._min_width > new_width:
            self._size.x = self._min_width

        elif new_width > self._max_width:
            self._size.x = self._max_width

        else:
            self._size.x = new_width


BOX = _Box()
