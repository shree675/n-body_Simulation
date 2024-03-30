import pygame
import math
import random
import time
import numpy as np

from simulation.body import Body
from simulation.util import Util

PI = math.pi


class Game:

    def __init__(self, n) -> None:
        self.num_bodies = n
        self.properties = []

        def initialize_params() -> None:
            pygame.init()
            self.screen_size = (1200, 780)
            self.screen_center = tuple([x / 2 for x in self.screen_size])
            self.frame_rate = 60
            self.boost_factor = 0.15
            self.clock = pygame.time.Clock()
            self.screen = pygame.display.set_mode(self.screen_size)
            self.surface = pygame.Surface(self.screen_size, pygame.SRCALPHA)
            self.font1 = pygame.font.SysFont("calibri", 20)
            self.font2 = pygame.font.SysFont("calibri", 15)

        def set_properties(n) -> list:
            bodies = [Body() for _ in range(n)]
            z = 0
            mass = 1000
            angle = -90
            radius = 100 if n <= 6 else 160 if n <= 12 else 220
            for body in bodies:
                x = radius * math.cos(PI * angle / 180) + self.screen_center[0]
                y = radius * math.sin(PI * angle / 180) + self.screen_center[1]
                body.position = (x, y, z)
                body.velocity = (0, 0, 0)
                body.mass = mass
                body.color = Util.get_random_color()
                angle += 360 / n
            return bodies

        initialize_params()
        self.bodies = set_properties(n)

    def compute_positions(self, prev_time) -> None:
        for body in self.bodies:
            ax = 0
            ay = 0
            az = 0
            for other_body in self.bodies:
                if other_body == body:
                    continue
                theta = 90 - math.degrees(
                    math.atan(
                        np.float64(body.position[0] - other_body.position[0])
                        and np.float64(body.position[1] - other_body.position[1])
                        / np.float64(body.position[0] - other_body.position[0])
                        or 0
                    )
                )
                phi = 90 - math.degrees(
                    math.atan(
                        np.float64(body.position[0] - other_body.position[0])
                        and np.float64(body.position[2] - other_body.position[2])
                        / np.float64(body.position[0] - other_body.position[0])
                        or 0
                    )
                )
                if (body.position[0] - other_body.position[0]) < 0:
                    theta = theta - 180
                    phi = phi - 180
                force = -Util.gravitational_force(body, other_body)
                ax += force * math.sin(PI * theta / 180)
                ay += force * math.cos(PI * theta / 180)
                az += force * math.cos(PI * phi / 180)
            vx = body.velocity[0] + ax * (time.time() - prev_time) * self.boost_factor
            vy = body.velocity[1] + ay * (time.time() - prev_time) * self.boost_factor
            vz = body.velocity[2] + az * (time.time() - prev_time) * self.boost_factor
            px = body.position[0] + vx * (time.time() - prev_time) * self.boost_factor
            py = body.position[1] + vy * (time.time() - prev_time) * self.boost_factor
            pz = body.position[2] + vz * (time.time() - prev_time) * self.boost_factor
            body.velocity = (vx, vy, vz)
            body.position = (px, py, pz)

    def render_bodies(self, trails) -> None:
        while len(trails) < self.num_bodies:
            trails.append([])
        for body in self.bodies:
            pygame.draw.circle(
                self.screen,
                body.color,
                (body.position[0], body.position[1]),
                Util.get_radius(body),
            )
            ind = self.bodies.index(body)
            trails[ind].append(body.position)
            for p in trails[ind]:
                self.surface.set_at(
                    (int(p[0]), int(p[1])), Util.opacity(body.color, p[2])
                )

    def render_background(self) -> None:
        pygame.draw.line(
            self.screen,
            Util.grey_color,
            (self.screen_size[0] - 20, self.screen_size[1] - 20),
            (self.screen_size[0] - 100, self.screen_size[1] - 100),
        )
        pygame.draw.line(
            self.screen,
            Util.grey_color,
            (self.screen_size[0] - 100, self.screen_size[1] - 100),
            (self.screen_size[0] - 100, self.screen_size[1] - 250),
        )
        pygame.draw.line(
            self.screen,
            Util.grey_color,
            (self.screen_size[0] - 100, self.screen_size[1] - 100),
            (self.screen_size[0] - 250, self.screen_size[1] - 100),
        )
        self.screen.blit(
            self.font2.render("y", True, Util.white_color),
            (self.screen_size[0] - 115, self.screen_size[1] - 265),
        )
        self.screen.blit(
            self.font2.render("z", True, Util.white_color),
            (self.screen_size[0] - 15, self.screen_size[1] - 15),
        )
        self.screen.blit(
            self.font2.render("-x", True, Util.white_color),
            (self.screen_size[0] - 265, self.screen_size[1] - 115),
        )

    def render_text(self, start_time) -> None:
        self.screen.blit(
            self.font1.render(
                "t: {}".format(time.time() - start_time), True, Util.white_color
            ),
            (10, self.screen_size[1] - 15),
        )
        self.screen.blit(
            self.font2.render(
                "Relative accuracy: {}%".format(
                    min(
                        100,
                        int(
                            100
                            - abs(self.clock.get_fps() - self.frame_rate)
                            / self.frame_rate
                            * 100
                        ),
                    )
                ),
                True,
                Util.white_color,
            ),
            (self.screen_size[0] - 150, 5),
        )

    def run(self) -> None:
        self.running = True
        trails = []
        start_time = time.time()

        while self.running:
            prev_time = time.time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
            self.clock.tick(self.frame_rate)

            self.screen.fill(Util.black_color)
            self.screen.blit(self.surface, (0, 0))

            self.render_background()
            self.compute_positions(prev_time)
            self.render_bodies(trails)
            self.render_text(start_time)

            pygame.display.flip()
