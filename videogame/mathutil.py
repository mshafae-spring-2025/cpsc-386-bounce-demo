
import pygame
from math import isclose, inf
from .circle import CircleSprite

def elastic_bounce(a, b):
    if not isinstance(a, CircleSprite):
        raise TypeError("c_a is not a CircleSprite")
    if not isinstance(b, CircleSprite):
        raise TypeError("c_b is not a CircleSprite")
    mass = (2.0 * b.mass) / (a.mass + b.mass)
    ab_velocity = a.velocity - b.velocity
    ab_center = a.position - b.position
    ab_v_dot_ab_c = ab_velocity.dot(ab_center)
    dist = ab_center.length_squared()
    assert(dist != 0.0)
    quot = ab_v_dot_ab_c / dist
    new_velocity = a.velocity - ((mass * quot) * ab_center)
    return new_velocity

def midpoint(a, b):
    assert isinstance(a, pygame.math.Vector2)
    assert isinstance(b, pygame.math.Vector2)
    return pygame.math.Vector2((a.x + b.x) / 2.0, (a.y + b.y) / 2.0)
