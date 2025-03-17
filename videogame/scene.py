"""Scene objects for making games with PyGame."""

from math import isclose, pi, cos, sin
from random import randint, uniform, choice
import pygame
from videogame import assets
from videogame import rgbcolors
from .circle import CircleSprite
from .mathutil import elastic_bounce, midpoint

# If you're interested in using abstract base classes, feel free to rewrite
# these classes.
# For more information about Python Abstract Base classes, see
# https://docs.python.org/3.8/library/abc.html


def random_position(max_width, max_height, buffer_space=0):
    return pygame.math.Vector2(
        randint(0 + buffer_space, max_width - (1 + buffer_space)),
        randint(0 + buffer_space, max_height - (1 + buffer_space)),
    )


def random_point_on_circle(center=pygame.math.Vector2(0, 0), radius=1.0):
    theta = uniform(0, (2 * pi))
    x = center.x + (radius * cos(theta))
    y = center.y + (radius * sin(theta))
    return pygame.math.Vector2(x, y)


def random_direction(center=pygame.math.Vector2(0, 0), radius=1.0):
    point = random_point_on_circle(center, radius)
    unit_direction = (point - center).normalize()
    return unit_direction


class Scene:
    """Base class for making PyGame Scenes."""

    def __init__(
        self, screen, background_color, screen_flags=None, soundtrack=None
    ):
        """Scene initializer"""
        self._screen = screen
        if not screen_flags:
            screen_flags = pygame.SCALED
        self._background = pygame.Surface(
            self._screen.get_size(), flags=screen_flags
        )
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
                pygame.mixer.music.set_volume(0.05)
            except pygame.error as pygame_error:
                print("\n".join(pygame_error.args))
                raise SystemExit("broken!!") from pygame_error
            pygame.mixer.music.play(loops=-1, fade_ms=500)

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


class BounceScene(PressAnyKeyToExitScene):
    """Inspired by the go_over_there.py demo included in the pygame source."""

    def __init__(self, screen, num_circles=10):
        super().__init__(
            screen, rgbcolors.black, soundtrack=assets.get('soundtrack')
        )
        self._delta_time = 0
        self._circles = []
        self.make_circles(num_circles)
        self._allsprites = pygame.sprite.RenderPlain(self._circles)
        self._pingpong_sounds = [
            pygame.mixer.Sound(assets.get('pingpong1')),
            pygame.mixer.Sound(assets.get('pingpong2')),
            pygame.mixer.Sound(assets.get('pingpong3')),
        ]
        for i in self._pingpong_sounds:
            i.set_volume(0.1)

    def make_circles(self, num_circles):
        print('Num circles', num_circles)
        circle_radius = 32
        buffer_between = circle_radius // 10
        (width, height) = self._screen.get_size()
        for i in range(num_circles):
            position = random_position(width, height, 5 * circle_radius)
            does_collide = [
                c.contains(position, buffer_between) for c in self._circles
            ]
            while any(does_collide) and len(self._circles) != 0:
                position = random_position(width, height, 5 * circle_radius)
                does_collide = [
                    c.contains(position, buffer_between) for c in self._circles
                ]

            rand_direction = random_direction(position, circle_radius)
            speed = uniform(CircleSprite.min_speed, CircleSprite.max_speed)
            assert position.x > 0 and position.x < width
            assert position.y > 0 and position.y < height
            c = CircleSprite(
                position,
                rand_direction,
                speed,
                circle_radius,
                rgbcolors.random_color(),
                i + 1,
            )
            self._circles.append(c)

    @property
    def delta_time(self):
        return self._delta_time

    @delta_time.setter
    def delta_time(self, val):
        self._delta_time = val

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.math.Vector2(event.pos)
            for circle in self._circles:
                if circle.rect.collidepoint(event.pos):
                    print(circle)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            for circle in self._circles:
                circle.switch_image()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            print('Reset...', end='', flush=True)
            num_circles = len(self._circles)
            self._circles = []
            self.make_circles(num_circles)
            self._allsprites = pygame.sprite.RenderPlain(self._circles)
            print('done.')
        else:
            super().process_event(event)

    def update_scene(self):
        super().update_scene()
        (width, height) = self._screen.get_size()
        # circle has to stay within the interval X: 0+radius, width-radius
        #                                        Y: 0+radius, height-radius
        import time

        for circle in self._circles:
            position = circle.position + (circle.velocity * self._delta_time)

            # Stay within the screen
            position.x = max(position.x, 0 + circle.radius)
            position.x = min(position.x, width - circle.radius)

            position.y = max(position.y, 0 + circle.radius)
            position.y = min(position.y, height - circle.radius)

            circle.position = position

        for circle in self._circles:
            normal = None
            if (circle.position.x - circle.radius) <= 0:
                normal = pygame.math.Vector2(1, 0)
            if (circle.position.x + circle.radius) >= width:
                normal = pygame.math.Vector2(-1, 0)
            if (circle.position.y - circle.radius) <= 0:
                normal = pygame.math.Vector2(0, 1)
            if (circle.position.y + circle.radius) >= height:
                normal = pygame.math.Vector2(0, -1)

            if normal:
                circle.direction = circle.direction.reflect(normal)

        for index, circle in enumerate(self._circles[:-1]):
            for other_circle in self._circles[index + 1 :]:
                assert circle != other_circle
                if pygame.sprite.collide_circle(circle, other_circle):
                    sound_effect = choice(self._pingpong_sounds)
                    sound_effect.play()

                    # Move them back to just touching
                    mid_pt = midpoint(circle.position, other_circle.position)
                    circle.position = (
                        mid_pt
                        + circle.radius
                        * (circle.position - other_circle.position).normalize()
                    )
                    other_circle.position = (
                        mid_pt
                        + other_circle.radius
                        * (other_circle.position - circle.position).normalize()
                    )

                    # Elastic Collision - https://en.wikipedia.org/wiki/Elastic_collision
                    # circle's new velocity
                    circle.velocity = elastic_bounce(circle, other_circle)
                    # other circle's new velocity - there is an error here
                    other_circle.velocity = -elastic_bounce(
                        other_circle, circle
                    )

        assert (
            circle.position.x >= 0 + circle.radius
            and circle.position.x <= width - circle.radius
        )
        assert (
            circle.position.y >= 0 + circle.radius
            and circle.position.y <= height - circle.radius
        )

    def render_updates(self):
        super().render_updates()
        self._allsprites.draw(self._screen)
