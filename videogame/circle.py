"""Circle Sprite"""

import pygame
from videogame import rgbcolors


class CircleSurface(pygame.Surface):
    """Class representing a circle with a bounding rect."""

    def __init__(
        self, radius, color, background_color=rgbcolors.black, name="None"
    ):
        width = 2 * radius
        super().__init__((width, width))
        # center in local surface coordinates
        center = (radius, radius)
        self._color = color
        self._name = name
        self.fill(background_color)
        # draw a circle in the center of the self surface
        pygame.draw.circle(self, self._color, center, radius)

    @property
    def radius(self):
        """Return the circle's radius"""
        return self._radius

    @property
    def rect(self):
        """Return bounding rect."""
        return self.get_rect()


class CircleSprite(pygame.sprite.Sprite):
    """The game's litle sprite balls/circles"""

    min_speed = 0.25
    max_speed = 5.0

    def __init__(self, position, speed, radius, color, name="None"):
        super().__init__()
        self.image = CircleSurface(radius, color, rgbcolors.black, name)
        self._original_position = position
        self.rect = self.image.rect
        # position is a Vector2
        self.rect.center = (position.x, position.y)
        # center in window coordinates
        # self._center = pygame.math.Vector2(center)
        assert speed <= CircleSprite.max_speed
        assert speed >= CircleSprite.min_speed
        self._speed = speed
        self._radius = radius
        # self._color = color
        self._name = name

    @property
    def radius(self):
        return self._radius

    @property
    def position(self):
        """Return the circle's position."""
        return pygame.math.Vector2(self.rect.center)

    @property
    def original_position(self):
        return self._original_position

    @position.setter
    def position(self, new_position):
        """Set the circle's position."""
        self.rect.center = (new_position.x, new_position.y)

    @property
    def speed(self):
        """Return the circle's speed."""
        return self._speed

    @property
    def inverse_speed(self):
        """The inverse speed which can't be slower than the min_speed"""
        return max(CircleSprite.max_speed - self._speed, CircleSprite.min_speed)

    def move_ip(self, x, y):
        """Move, in-place"""
        self.position = self.position + pygame.math.Vector2(x, y)

    def contains(self, point, buffer=0):
        """Return true if point is in the circle + buffer"""
        v = point - self.position
        distance = v.length()
        # assume all circles have the same radius
        seperating_distance = 2 * (self.radius + buffer)
        return distance <= seperating_distance

    def __repr__(self):
        """CircleSprite stringify."""
        return f'CircleSprite({repr(self.position)}, {self.speed}, {self.radius}, {self._color}, "{self._name}")'
