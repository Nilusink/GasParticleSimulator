"""
main.py
24. May 2024

A gaß particle simulator

Author:
Nilusink
"""
from contextlib import suppress
from subprocess import Popen
from threading import Thread
from vectors import Vec2
import typing as tp
import numpy as np
import socket
import pygame
import random
import json
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
INITIAL_PARTICLE_COUNT = 60
PARTICLE_RADIUS_RANGE = (5, 10)
PARTICLE_SPEED = 2
FPS = 60

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gas Particle Simulation")


class _Box:
    def __init__(self) -> None:
        self._pos = Vec2.from_cartesian(100, 100)
        self._size = Vec2.from_cartesian(600, 600)

    @property
    def pos(self) -> Vec2:
        return self._pos.copy()

    @property
    def size(self) -> Vec2:
        return self._size.copy()

    @property
    def left(self) -> int:
        return self._pos.x

    @property
    def right(self) -> int:
        return self._pos.x + self.size.x

    @property
    def top(self) -> int:
        return self._pos.y

    @property
    def bottom(self) -> int:
        return self._pos.y + self.size.y

    def draw(self, screen) -> None:
        pygame.draw.rect(
            screen,
            (0, 0, 0, 255),
            pygame.rect.Rect(self.pos.xy, self.size.xy),
            3
        )


BOX = _Box()


class Particles(list):
    def __init__(self) -> None:
        super().__init__()

    def change_particles(self, count: int) -> None:
        """
        create or delete multiple particles
        """
        for _ in range(count):
            self.add_particle()

        for _ in range(0, count, -1):
            self.remove_particle()

    def add_particle(self) -> None:
        """
        add a single particle
        """
        x = random.randint(BOX.left + 30, BOX.right - 30)
        y = random.randint(BOX.top + 30, BOX.bottom - 30)

        radius = random.choice([7, 15])

        angle = random.uniform(0, 2 * math.pi)
        color = {7: (255, 0, 0), 15: (0, 0, 255)}[radius]
        self.append(Particle(
            x,
            y,
            radius,
            self.get_av_speed(),
            angle,
            color
        ))

    def remove_particle(self) -> None:
        """
        remove a single particle
        """
        if self:
            self.pop()

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
            return PARTICLE_SPEED

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
    def __init__(self, x, y, radius, speed, angle, color):
        self.position = Vec2.from_cartesian(x, y)
        self.velocity = Vec2.from_polar(angle, speed)
        self.radius = radius
        self.color = color
        self.mass = radius**2

    def move(self):
        self.position += self.velocity

        # Bounce off the walls
        if self.position.x - self.radius < BOX.left or self.position.x + self.radius > BOX.right:
            self.velocity.angle = math.pi - self.velocity.angle
            self.position.x = max(self.radius, min(self.position.x, WIDTH - self.radius))

        if self.position.y - self.radius < BOX.top or self.position.y + self.radius > BOX.bottom:
            self.velocity.angle = -self.velocity.angle
            self.position.y = max(self.radius, min(self.position.y, HEIGHT - self.radius))

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
        pygame.draw.circle(screen, self.color, self.position.xy, self.radius)

    def collide(self, other: tp.Self):
        delta = self.position - other.position
        distance = math.hypot(*delta.xy)

        if distance < self.radius + other.radius:
            # move other out of way
            # other.position += Vec2.from_polar(delta.angle, (self.radius-distance) + 1)

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


class Communicator:
    running: bool = True

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((self.host, self.port))
        self._socket.settimeout(1)

        Thread(target=self.receive).start()

    def receive(self) -> None:
        """
        receive settings
        """
        while self.running:
            try:
                msg, addr = self._socket.recvfrom(1024)
                data = json.loads(msg.decode('utf-8'))

            except (TimeoutError, json.JSONDecodeError):
                continue

            # parse request
            answer: dict = {}
            for key in data:
                match key:
                    case "vel":
                        particles.multiply_speeds(data["vel"])

                    case "rvel":
                        answer["vel"] = particles.get_av_speed()

                    case "num":
                        particles.change_particles(data["num"])

                    case "rnum":
                        answer["num"] = len(particles)

                    case _:
                        print(f"INVALID KEY: \"{key}\"")

            # if anything has been requested, send answer
            if answer:
                # we don't care if there was an error sending, so just ignore
                # all possible errors
                with suppress(Exception):
                    self._socket.sendto(json.dumps(answer).encode('utf-8'), addr)


# global variables
particles = Particles()


def main() -> None:
    running = True
    clock = pygame.time.Clock()
    particles.change_particles(INITIAL_PARTICLE_COUNT)

    comm = Communicator("127.0.0.1", 24323)

    # start settings GUI
    Popen(f"{sys.executable} settings_gui.py")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                comm.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    particles.multiply_speeds(1.1)

                elif event.key == pygame.K_DOWN:
                    particles.multiply_speeds(.9)

                elif event.key == pygame.K_a:
                    particles.add_particle()

                elif event.key == pygame.K_r:
                    particles.remove_particle()

        screen.fill(WHITE)
        for i, particle in enumerate(particles):
            particle.move()

            for other in particles[i + 1:]:
                particle.collide(other)

            particle.draw(screen)

        BOX.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
