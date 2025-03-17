"""Circle Sprite"""

import pygame
from videogame import assets
from videogame import rgbcolors
from random import uniform

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
        self.set_colorkey(background_color)
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

    min_speed = 0.1
    max_speed = 0.7

    def __init__(self, position, direction, speed, radius, color, name="None"):
        super().__init__()
        self._circle_image = CircleSurface(radius, color, rgbcolors.black, name)
        self._png_image = pygame.image.load(assets.get('spriteimg'))
        self.image = self._png_image
        self._png_is_on = True
        self._original_position = position
        self.rect = self.image.get_rect()
        # position is a Vector2
        self.rect.center = (position.x, position.y)
        # center in window coordinates
        # self._center = pygame.math.Vector2(center)
        self._direction = direction
        assert speed <= CircleSprite.max_speed
        assert speed >= CircleSprite.min_speed
        self._speed = speed
        self._radius = radius
        self._color = color
        self._name = name

    def switch_image(self):
        if self._png_is_on:
            self.image = self._circle_image
            self._png_is_on = False
        else:
            self.image = self._png_image
            self._png_is_on = True
    
    @property
    def radius(self):
        return self._radius

    @property
    def position(self):
        """Return the circle's position."""
        return pygame.math.Vector2(self.rect.center)

    @position.setter
    def position(self, new_position):
        """Set the circle's position."""
        if not isinstance(new_position, pygame.math.Vector2):
            raise TypeError("new_direction doesn't match self._direction")
        self.rect.center = (new_position.x, new_position.y)

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, new_direction):
        if not isinstance(new_direction, type(self._direction)):
            raise TypeError("new_direction doesn't match self._direction")
        self._direction = new_direction

    @property
    def speed(self):
        """Return the circle's speed."""
        return self._speed

    @property
    def velocity(self):
        return self._direction * self._speed
    
    @velocity.setter
    def velocity(self, new_velocity):
        if not isinstance(new_velocity, pygame.math.Vector2):
            raise TypeError("new_direction doesn't match self._direction")
        self._speed = new_velocity.length()
        self._direction = new_velocity.normalize()
    
    @property
    def mass(self):
        return 1.0
    
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
