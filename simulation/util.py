import pygame
import random
import numpy as np


class Util:

    black_color = pygame.Color(10, 10, 10)
    white_color = pygame.Color(200, 200, 200)
    grey_color = pygame.Color(80, 80, 80)

    @staticmethod
    def get_random_color() -> pygame.Color:
        return pygame.Color(*[50 + random.randint(0, 200) for _ in range(3)])

    @staticmethod
    def gravitational_force(body, other_body) -> float:
        r = np.linalg.norm(np.array(body.position) - np.array(other_body.position))
        return body.mass * other_body.mass / max(r, 25)

    @staticmethod
    def get_radius(body) -> float:
        return max(1, 7 + body.position[2] / 200)

    @staticmethod
    def opacity(color, pz) -> pygame.Color:
        opacity = max(0.1, min(0.8, 0.5 + pz / 200))
        color.a = int(255 * opacity)
        return color
