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
import socket
import pygame
import json
import sys

from physics_calculations import pressure_from_particles, calculate_temperature
from particles import particles
from box import BOX

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
INITIAL_PARTICLE_COUNT = 60
PARTICLE_RADIUS_RANGE = (5, 10)
FPS = 60

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gas Particle Simulation")
BOX.world_size = WIDTH, HEIGHT


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

            # send close if not running anymore
            if not self.running:
                self._socket.sendto(json.dumps({
                    "close": 1
                }).encode('utf-8'), addr)

            # parse request
            answer: dict = {}
            for key in data:
                match key:
                    case "vel":
                        particles.multiply_speeds(data["vel"])

                    case "len":
                        BOX.set_length(data["len"])

                    case "rvel":
                        answer["vel"] = particles.get_av_energy()

                    case "num":
                        particles.change_particles(data["num"])

                    case "rnum":
                        answer["num"] = len(particles)

                    case "rstats":
                        p = pressure_from_particles(
                            particles, BOX.volume
                        )
                        t = calculate_temperature(
                            particles,
                            BOX.volume,
                            p
                        )
                        answer["stats"] = {
                            "p": p,
                            "t": t,
                            "l": BOX.size.x
                        }

                    case _:
                        print(f"INVALID KEY: \"{key}\"")

            # if anything has been requested, send answer
            if answer:
                # we don't care if there was an error sending, so just ignore
                # all possible errors
                with suppress(Exception):
                    self._socket.sendto(
                        json.dumps(answer).encode('utf-8'), addr
                    )


def main() -> None:
    running = True
    clock = pygame.time.Clock()
    particles.change_particles(INITIAL_PARTICLE_COUNT, False)

    comm = Communicator("127.0.0.1", 24323)

    # start settings GUI
    Popen(f"{sys.executable} settings_gui.py")

    while running:
        # handle pygame events
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

        # update and draw particles
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
