
"""Scene objects for making games with PyGame."""

import math
import os
import pygame
from videogame import rgbcolors
from random import randint, uniform
from videogame import assets

# If you're interested in using abstract base classes, feel free to rewrite
# these classes.
# For more information about Python Abstract Base classes, see
# https://docs.python.org/3.8/library/abc.html

def random_position(max_width, max_height):
    return pygame.math.Vector2(randint(0, max_width-1), randint(0, max_height-1))

class Scene:
    """Base class for making PyGame Scenes."""

    def __init__(self, screen, background_color, soundtrack=None):
        """Scene initializer"""
        self._screen = screen
        self._background = pygame.Surface(self._screen.get_size())
        self._background.fill(background_color)
        self._frame_rate = 60
        self._is_valid = True
        self._soundtrack = soundtrack
        self._render_updates = None

    def draw(self):
        """Draw the scene."""
        self._screen.blit(self._background, (0, 0))

    def process_event(self, event):
        """Process a game event by the scene."""
        # This should be commented out or removed since it generates a lot of noise.
        # print(str(event))
        if event.type == pygame.QUIT:
            print("Good Bye!")
            self._is_valid = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            print("Bye bye!")
            self._is_valid = False

    def is_valid(self):
        """Is the scene valid? A valid scene can be used to play a scene."""
        return self._is_valid

    def render_updates(self):
        """Render all sprite updates."""

    def update_scene(self):
        """Update the scene state."""

    def start_scene(self):
        """Start the scene."""
        if self._soundtrack:
            try:
                pygame.mixer.music.load(self._soundtrack)
                pygame.mixer.music.set_volume(0.5)
            except pygame.error as pygame_error:
                print("\n".join(pygame_error.args))
                raise SystemExit("broken!!") from pygame_error
            pygame.mixer.music.play(-1)

    def end_scene(self):
        """End the scene."""
        if self._soundtrack and pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(500)
            pygame.mixer.music.stop()

    def frame_rate(self):
        """Return the frame rate the scene desires."""
        return self._frame_rate


class PressAnyKeyToExitScene(Scene):
    """Empty scene where it will invalidate when a key is pressed."""

    def process_event(self, event):
        """Process game events."""
        super().process_event(event)
        if event.type == pygame.KEYDOWN:
            self._is_valid = False


class Circle:
    """Class representing a ball with a bounding rect."""
    min_speed = 0.25
    max_speed = 5.0
    def __init__(self, position, speed, radius, color, name="None"):
        self._position = position
        self._original_position = pygame.math.Vector2(position)
        assert speed <= Circle.max_speed
        assert speed >= Circle.min_speed
        self._speed = speed
        self._radius = radius
        self._color = color
        self._name = name

    @property
    def radius(self):
        """Return the circle's radius"""
        return self._radius

    @property
    def position(self):
        """Return the circle's position."""
        return self._position

    @property
    def original_position(self):
        return self._original_position

    @position.setter
    def position(self, val):
        """Set the circle's position."""
        self._position = val

    @property
    def speed(self):
        """Return the circle's speed."""
        return self._speed

    @property
    def inverse_speed(self):
        return Circle.max_speed - self._speed
    
    def move_ip(self, x, y):
        self._position = self._position + pygame.math.Vector2(x, y)
    
    @property
    def rect(self):
        """Return bounding rect."""
        left = self._position.x - self._radius
        top = self._position.y - self._radius
        width = 2 * self._radius
        return pygame.Rect(left, top, width, width)

    @property
    def width(self):
        """Return the width of the bounding box the circle is in."""
        return 2 * self._radius

    @property
    def height(self):
        """Return the height of the bounding box the circle is in."""
        return 2 * self._radius

    def contains(self, point, buffer=0):
        """Return true if point is in the circle + buffer"""
        v = point - self._position
        distance = v.length()
        # assume all circles have the same radius
        seperating_distance = 2 * (self._radius + buffer)
        return distance <= seperating_distance

    def draw(self, screen):
        """Draw the circle to screen."""
        pygame.draw.circle(screen, self._color, self.position, self.radius)

    def __repr__(self):
        """Circle stringify."""
        return f'Circle({repr(self._position)}, {self._radius}, {self._color}, "{self._name}")'

class MoveScene(PressAnyKeyToExitScene):
    """Inspired by the go_over_there.py demo included in the pygame source."""
    def __init__(self, screen):
        super().__init__(screen, rgbcolors.black, None)
        self._target_position = None
        self._delta_time = 0
        self._circles = []
        self.make_circles()
        self._sucking_sound = pygame.mixer.Sound(assets.get('suck3'))
        self._explosion_sound = pygame.mixer.Sound(assets.get('explosion'))

    def make_circles(self):
        num_circles = 1000
        circle_radius = 5
        buffer_between = 3
        (width, height) = self._screen.get_size()
        for i in range(num_circles):
            position = random_position(width, height)
            does_collide = [c.contains(position, buffer_between) for c in self._circles]
            while any(does_collide) and len(self._circles):
                position = random_position(width, height)
                does_collide = [c.contains(position, buffer_between) for c in self._circles]

            speed = uniform(Circle.min_speed, Circle.max_speed)
            c = Circle(position, speed, circle_radius, rgbcolors.random_color(), i+1)
            self._circles.append(c)
    
    @property
    def delta_time(self):
        return self._delta_time
    
    @delta_time.setter
    def delta_time(self, val):
        self._delta_time = val
    
    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._target_position:
                self._target_position = None
                print('Going home.')
                self._explosion_sound.play()
            else:
                self._target_position = pygame.math.Vector2(event.pos)
                print(f'Target position is {self._target_position}')
                self._sucking_sound.play()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            print('Reset...', end='', flush=True)
            self._target_position = None
            self._circles = []
            self.make_circles()
            print('done.')
        else:
            super().process_event(event)
    
    def update_scene(self):
        super().update_scene()
        if self._target_position:
            for c in self._circles:
                if True:
                    c.position.move_towards_ip(self._target_position, c.speed * self._delta_time)
                else:
                    max_distance = c.speed * self._delta_time
                    if math.isclose(max_distance, 0.0, rel_tol=1e-01):
                        continue
                    direction = self._target_position - c.position
                    distance = direction.length()
                    if math.isclose(distance, 0.0, rel_tol=1e-01):
                        continue
                    elif distance <= max_distance:
                        c.position = self._target_position
                    else:
                        movement = direction * (max_distance / distance)
                        c.move_ip(movement.x, movement.y)
        else:
            for c in self._circles:
                c.position.move_towards_ip(c.original_position, c.inverse_speed * self._delta_time)

    def draw(self):
        super().draw()
        for c in self._circles:
            c.draw(self._screen)