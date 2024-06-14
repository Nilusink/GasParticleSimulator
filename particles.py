"""
particles.py
1. June 2024

Thermodynamics for the simulator

Author:
Nilusink
"""
from physics_calculations import pressure_from_particles, calculate_temperature
from vectors import Vec2
from box import BOX
import pygame as pg
import typing as tp
import numpy as np
import random
import math


class Particles(list):
    def __init__(self) -> None:
        super().__init__()

    def change_particles(self, count: int, recalculate: bool = True) -> None:
        """
        create or delete multiple particles
        """
        for _ in range(count):
            self.add_particle(recalculate)

        for _ in range(0, count, -1):
            self.remove_particle(recalculate)

    def add_particle(self, recalculate: bool = True) -> None:
        """
        add a single particle
        """
        x = random.randint(BOX.left + 30, BOX.right - 30)
        y = random.randint(BOX.top + 30, BOX.bottom - 30)

        radius = random.choice([7, 15])

        angle = random.uniform(0, 2 * math.pi)
        color = {7: (255, 0, 0), 15: (0, 0, 255)}[radius]
        mass = {7: 7*10**(-23), 15: 15*10**(-23)}[radius]

        bevore_press = pressure_from_particles(self, BOX.volume)

        self.append(Particle(
            x,
            y,
            mass,
            radius,
            self.get_av_speed(),
            angle,
            color
        ))

        if recalculate:
            BOX.recalculate_from_pressure(bevore_press, self)

    def remove_particle(self, recalculate: bool = True) -> None:
        """
        remove a single particle
        """
        # cant remove last particle bcuz
        if len(self) > 1:
            bevore_press = pressure_from_particles(self, BOX.volume)
            self.pop()

            if recalculate:
                BOX.recalculate_from_pressure(bevore_press, self)

    def multiply_speeds(self, mult: float) -> None:
        """
        multiply all particle speeds
        """
        for particle in self:
            particle.velocity *= mult

    def get_av_speed(self) -> float:
        """
        get the average particle speed
        """
        speeds = [p.velocity.length for p in self]

        if len(speeds) == 0:
            return 2

        return sum(speeds) / len(speeds)

    def get_av_energy(self) -> float:
        """
        average particle energy
        """
        speeds = [p.velocity.length * p.mass for p in self]

        if len(speeds) == 0:
            return 0

        return sum(speeds) / len(speeds)


# Particle class
class Particle:
    def __init__(self, x, y, mass, radius, speed, angle, color):
        self.position: Vec2 = Vec2.from_cartesian(x, y)
        self.velocity: Vec2 = Vec2.from_polar(angle, speed)
        self.radius = radius
        self.color = color
        self.mass = mass

    def move(self):
        self.position += self.velocity

        # Bounce off the walls
        if self.position.x - self.radius < BOX.left or self.position.x + self.radius > BOX.right:
            self.velocity.angle = math.pi - self.velocity.angle
            self.position.x = max(self.radius, min(
                self.position.x, BOX.world_width - self.radius
            ))

        if self.position.y - self.radius < BOX.top or self.position.y + self.radius > BOX.bottom:
            self.velocity.angle = -self.velocity.angle
            self.position.y = max(self.radius, min(
                self.position.y, BOX.world_height - self.radius
            ))

        # check if oob
        if self.position.x - self.radius <= BOX.left:
            self.position.x = BOX.left + self.radius + 1

        elif self.position.x + self.radius >= BOX.right:
            self.position.x = BOX.right - (self.radius + 1)

        if self.position.y - self.radius <= BOX.top:
            self.position.y = BOX.top + self.radius + 1

        elif self.position.y + self.radius >= BOX.bottom:
            self.position.y = BOX.bottom - (self.radius + 1)

    def draw(self, screen):
        pg.draw.circle(screen, self.color, self.position.xy, self.radius+1)

    def collide(self, other: tp.Self):
        delta = self.position - other.position
        distance = math.hypot(*delta.xy)

        if distance < self.radius + other.radius:
            # move other out of way
            other.position = self.position - Vec2.from_polar(delta.angle, self.radius+other.radius)

            # split the velocities in two directions (90°)
            a = delta.angle - self.velocity.angle

            now_carry = Vec2.from_polar(
                angle=delta.angle - math.pi / 2,
                length=self.velocity.length * np.sin(a)
            )
            now_collision = Vec2.from_polar(
                angle=delta.angle,
                length=self.velocity.length * np.cos(a)
            )

            a = delta.angle - other.velocity.angle
            inf_carry = Vec2.from_polar(
                angle=delta.angle - math.pi / 2,
                length=other.velocity.length * np.sin(a)
            )
            inf_collision = Vec2.from_polar(
                angle=delta.angle,
                length=other.velocity.length * np.cos(a)
            )

            now_v = now_collision.length * self.mass
            now_v += (inf_collision.length * 2 - now_collision.length) * other.mass
            now_v /= self.mass + other.mass

            inf_v = inf_collision.length * other.mass
            inf_v += (now_collision.length * 2 - inf_collision.length) * self.mass
            inf_v /= other.mass + self.mass

            now_v = now_carry + Vec2.from_polar(angle=now_collision.angle, length=now_v)
            inf_v = inf_carry + Vec2.from_polar(angle=inf_collision.angle, length=inf_v)

            # assign velocities to objects
            self.velocity = now_v
            other.velocity = inf_v


# global variables
particles = Particles()
