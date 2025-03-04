"""Scene objects for making games with PyGame."""

from math import isclose
from random import randint, uniform
import pygame
from videogame import assets
from videogame import rgbcolors
from .circle import CircleSprite

# If you're interested in using abstract base classes, feel free to rewrite
# these classes.
# For more information about Python Abstract Base classes, see
# https://docs.python.org/3.8/library/abc.html


def random_position(max_width, max_height):
    return pygame.math.Vector2(
        randint(0, max_width - 1), randint(0, max_height - 1)
    )


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


class MoveScene(PressAnyKeyToExitScene):
    """Inspired by the go_over_there.py demo included in the pygame source."""

    def __init__(self, screen, num_circles=1000):
        super().__init__(
            screen, rgbcolors.black, soundtrack=assets.get('soundtrack')
        )
        self._target_position = None
        self._delta_time = 0
        self._circles = []
        self.make_circles(num_circles)
        self._allsprites = pygame.sprite.RenderPlain(self._circles)
        self._sucking_sound = None
        self._explosion_sound = pygame.mixer.Sound(assets.get('explosion'))
        self._explosion_sound.set_volume(0.1)

    @property
    def sucking_sound(self):
        self._sucking_sound = pygame.mixer.Sound(
            assets.get(f'suck{randint(1,3)}')
        )
        self._sucking_sound.set_volume(0.25)
        return self._sucking_sound

    def make_circles(self, num_circles):
        # num_circles = 1000
        print('Num circles', num_circles)
        circle_radius = 5
        buffer_between = 3
        (width, height) = self._screen.get_size()
        for i in range(num_circles):
            position = random_position(width, height)
            does_collide = [
                c.contains(position, buffer_between) for c in self._circles
            ]
            while any(does_collide) and len(self._circles) != 0:
                position = random_position(width, height)
                does_collide = [
                    c.contains(position, buffer_between) for c in self._circles
                ]

            speed = uniform(CircleSprite.min_speed, CircleSprite.max_speed)
            c = CircleSprite(
                position, speed, circle_radius, rgbcolors.random_color(), i + 1
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
            if self._target_position:
                self._target_position = None
                print('Going home.')
                self._explosion_sound.play()
            else:
                self._target_position = pygame.math.Vector2(event.pos)
                print(f'Target position is {self._target_position}')
                self.sucking_sound.play()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            print('Reset...', end='', flush=True)
            self._target_position = None
            num_circles = len(self._circles)
            self._circles = []
            self.make_circles(num_circles)
            self._allsprites = pygame.sprite.RenderPlain(self._circles)
            print('done.')
        else:
            super().process_event(event)

    def update_scene(self):
        super().update_scene()
        if self._target_position:
            for c in self._circles:
                if True:
                    # Can't use move_towards_ip because c.position is a property converting the
                    # sprite's rect center.
                    c.position = c.position.move_towards(
                        self._target_position, c.speed * self._delta_time
                    )
                else:
                    max_distance = c.speed * self._delta_time
                    if isclose(max_distance, 0.0, rel_tol=1e-01):
                        continue
                    direction = self._target_position - c.position
                    distance = direction.length()
                    if isclose(distance, 0.0, rel_tol=1e-01):
                        continue
                    elif distance <= max_distance:
                        c.position = self._target_position
                    else:
                        movement = direction * (max_distance / distance)
                        c.move_ip(movement.x, movement.y)
        else:
            for c in self._circles:
                # Can't use move_towards_ip because c.position is a property converting the
                # sprite's rect center.
                c.position = c.position.move_towards(
                    c.original_position, c.inverse_speed * self._delta_time
                )

    # def draw(self):
    #     super().draw()

    def render_updates(self):
        super().render_updates()
        self._allsprites.draw(self._screen)
