
import math
import random
import sys      
from abc import ABC, abstractmethod     

import pygame

class Settings:

    WIDTH = 1900                 
    HEIGHT = 1080                
    FPS = 60                    
    GAME_DURATION = 60          
    CORRECT_PER_LEVEL = 5       
    MAX_VARIETY = 4             
    MATCH_CHANCE = 0.5          
    FEEDBACK_TIME = 0.35        


    BASE_POINTS = 10            
    WRONG_PENALTY = 5           


    BG = (30, 34, 54)
    PANEL = (45, 52, 80)
    WHITE = (240, 240, 240)
    GREEN = (80, 200, 120)
    RED = (220, 90, 90)


    CARD_COLORS = [
        (235, 87, 87),     
        (86, 160, 235),    
        (250, 200, 70),    
        (120, 210, 130),   
    ]

class Shape(ABC):


    @abstractmethod
    def draw(self, surface, color, center, size):
        """کشیدن شکل روی سطح مورد نظر."""


    def __eq__(self, other):
        return type(self) is type(other)

    def __hash__(self):
        return hash(type(self))


class Circle(Shape):
    def draw(self, surface, color, center, size):
        pygame.draw.circle(surface, color, center, size)


class Square(Shape):
    def draw(self, surface, color, center, size):
        cx, cy = center
        pygame.draw.rect(surface, color, (cx - size, cy - size, size * 2, size * 2))


class Triangle(Shape):
    def draw(self, surface, color, center, size):
        cx, cy = center
        points = [(cx, cy - size), (cx - size, cy + size), (cx + size, cy + size)]
        pygame.draw.polygon(surface, color, points)


class Diamond(Shape):
    def draw(self, surface, color, center, size):
        cx, cy = center
        points = [(cx, cy - size), (cx + size, cy), (cx, cy + size), (cx - size, cy)]
        pygame.draw.polygon(surface, color, points)

class Card:

    def __init__(self, shape, color):

        self._shape = shape
        self._color = color

    @property
    def shape(self):
        return self._shape

    @property
    def color(self):
        return self._color

    def matches(self, other):
        return self._shape == other.shape and self._color == other.color

    def draw(self, surface, center, size=70):
        self._shape.draw(surface, self._color, center, size)

class CardFactory:

    def __init__(self, shapes, colors):
        self._shapes = shapes      
        self._colors = colors      

    def create_random(self, variety):
        shape = random.choice(self._shapes[:variety])
        color = random.choice(self._colors[:variety])
        return Card(shape, color)

    def create_next(self, previous, variety, match_chance):

        if previous is not None and random.random() < match_chance:
            return Card(previous.shape, previous.color)
        return self.create_random(variety)





class LevelManager:

    def __init__(self, correct_per_level, max_variety):
        self._correct_per_level = correct_per_level
        self._max_variety = max_variety
        self._correct_count = 0

    def register_correct(self):
        self._correct_count += 1

    @property
    def level(self):
        return 1 + self._correct_count // self._correct_per_level

    @property
    def variety(self):
        return min(self.level + 1, self._max_variety)


class ScoreBoard:

    def __init__(self):
        self._best = 0          
        self.reset()

    def reset(self):
        self._score = 0
        self._streak = 0
        self._correct = 0
        self._total = 0

    def register_correct(self):
        self._correct += 1
        self._total += 1
        self._streak += 1

        self._score += Settings.BASE_POINTS + self._streak

    def register_wrong(self):
        self._total += 1
        self._streak = 0
        self._score = max(0, self._score - Settings.WRONG_PENALTY)

    def finish(self):
        self._best = max(self._best, self._score)

    @property
    def score(self):
        return self._score

    @property
    def best(self):
        return self._best

    @property
    def correct(self):
        return self._correct

    @property
    def total(self):
        return self._total

    @property
    def accuracy(self):
        return (self._correct / self._total * 100) if self._total else 0


class Timer:

    def __init__(self, duration):
        self._duration = duration
        self._remaining = duration

    def reset(self):
        self._remaining = self._duration

    def update(self, dt):
        self._remaining = max(0, self._remaining - dt)

    @property
    def finished(self):
        return self._remaining <= 0

    @property
    def display_seconds(self):
        return math.ceil(self._remaining)


class FeedbackFlash:

    def __init__(self, duration):
        self._duration = duration
        self._timer = 0
        self._color = None

    def trigger(self, color):
        self._color = color
        self._timer = self._duration

    def update(self, dt):
        if self._timer > 0:
            self._timer -= dt

    def reset(self):
        self._timer = 0
        self._color = None

    def current_color(self, default):
        return self._color if self._timer > 0 else default

class TextRenderer:

    def __init__(self):

        self._fonts = {
            "big": pygame.font.Font(None, 72),
            "normal": pygame.font.Font(None, 40),
            "small": pygame.font.Font(None, 28),
        }

    def draw(self, surface, text, size, center, color=Settings.WHITE):
        label = self._fonts[size].render(text, True, color)
        surface.blit(label, label.get_rect(center=center))


class Button:

    def __init__(self, rect, text, color):
        self._rect = pygame.Rect(rect)
        self._text = text
        self._color = color

    def draw(self, surface, text_renderer):
        pygame.draw.rect(surface, self._color, self._rect, border_radius=12)
        text_renderer.draw(surface, self._text, "normal", self._rect.center)

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self._rect.collidepoint(event.pos))

class Scene(ABC):
    
    def __init__(self, game):
        self._game = game      

    def on_enter(self):
        """هر بار که این صحنه فعال می‌شه صدا زده می‌شه."""

    @abstractmethod
    def handle_event(self, event):
        """پردازش یک رویداد (کلیک، کلید و...)."""

    def update(self, dt):
        """به‌روزرسانی منطق؛ پیش‌فرض کاری نمی‌کنه."""

    @abstractmethod
    def draw(self, surface):
        """رسم صحنه روی صفحه."""


class MenuScene(Scene):

    def __init__(self, game):
        super().__init__(game)
        self._start_button = Button((300, 350, 200, 70), "Start", Settings.GREEN)

    def handle_event(self, event):
        space_pressed = event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
        if self._start_button.is_clicked(event) or space_pressed:
            self._game.change_scene("play")

    def draw(self, surface):
        text = self._game.text
        cx = Settings.WIDTH // 2
        text.draw(surface, "Speed Match", "big", (cx, 150))
        text.draw(surface, "Is the card the same as the previous one?", "normal", (cx, 240))
        text.draw(surface, "Keys: Left arrow = Different, Right arrow = Match", "small", (cx, 290))
        self._start_button.draw(surface, text)
        text.draw(surface, f"Best score: {self._game.scoreboard.best}", "small", (cx, 470))


class PlayScene(Scene):

    def __init__(self, game):
        super().__init__(game)

        self._factory = CardFactory([Circle(), Square(), Triangle(), Diamond()],
                                    Settings.CARD_COLORS)
        self._levels = LevelManager(Settings.CORRECT_PER_LEVEL, Settings.MAX_VARIETY)
        self._timer = Timer(Settings.GAME_DURATION)
        self._flash = FeedbackFlash(Settings.FEEDBACK_TIME)
        self._diff_button = Button((130, 470, 240, 80), "Different (<-)", Settings.RED)
        self._match_button = Button((430, 470, 240, 80), "Match (->)", Settings.GREEN)
        self._previous = None
        self._current = None

    def on_enter(self):
        self._game.scoreboard.reset()
        self._levels = LevelManager(Settings.CORRECT_PER_LEVEL, Settings.MAX_VARIETY)
        self._timer.reset()
        self._flash.reset()
        self._previous = None
        self._current = self._factory.create_random(self._levels.variety)

    def _answer(self, says_match):
        board = self._game.scoreboard
        if self._previous is not None:
            actually_match = self._current.matches(self._previous)
            if actually_match == says_match:
                board.register_correct()
                self._levels.register_correct()
                self._flash.trigger(Settings.GREEN)
            else:
                board.register_wrong()
                self._flash.trigger(Settings.RED)

        self._previous = self._current
        self._current = self._factory.create_next(
            self._previous, self._levels.variety, Settings.MATCH_CHANCE)

    def handle_event(self, event):
        is_key = event.type == pygame.KEYDOWN
        if self._match_button.is_clicked(event) or (is_key and event.key == pygame.K_RIGHT):
            self._answer(True)
        elif self._diff_button.is_clicked(event) or (is_key and event.key == pygame.K_LEFT):
            self._answer(False)

    def update(self, dt):
        self._timer.update(dt)
        self._flash.update(dt)
        if self._timer.finished:

            self._game.scoreboard.finish()
            self._game.change_scene("result")

    def draw(self, surface):
        text = self._game.text
        board = self._game.scoreboard

        text.draw(surface, f"Time: {self._timer.display_seconds}", "normal", (120, 40))
        text.draw(surface, f"Score: {board.score}", "normal", (Settings.WIDTH // 2, 40))
        text.draw(surface, f"Level: {self._levels.level}", "normal", (Settings.WIDTH - 120, 40))

        panel = pygame.Rect(0, 0, 300, 300)
        panel.center = (Settings.WIDTH // 2, 250)
        panel_color = self._flash.current_color(Settings.PANEL)
        pygame.draw.rect(surface, panel_color, panel, border_radius=20)
        self._current.draw(surface, panel.center)

        if self._previous is None:
            text.draw(surface, "Memorize this card, then press any answer", "small",
                      (Settings.WIDTH // 2, 430))

        self._diff_button.draw(surface, text)
        self._match_button.draw(surface, text)


class ResultScene(Scene):

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_RETURN, pygame.K_r):
            self._game.change_scene("play")       
        elif event.key == pygame.K_ESCAPE:
            self._game.quit()

    def draw(self, surface):
        text = self._game.text
        board = self._game.scoreboard
        cx = Settings.WIDTH // 2
        text.draw(surface, "Time's up!", "big", (cx, 130))
        text.draw(surface, f"Score: {board.score}", "normal", (cx, 250))
        text.draw(surface, f"Best: {board.best}", "normal", (cx, 300))
        text.draw(surface, f"Accuracy: {board.accuracy:.0f}%  ({board.correct}/{board.total})",
                  "normal", (cx, 350))
        text.draw(surface, "Press Enter to play again, Esc to quit", "small", (cx, 450))

class Game:

    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode((Settings.WIDTH, Settings.HEIGHT))
        pygame.display.set_caption("Speed Match - Prototype")
        self._clock = pygame.time.Clock()

        self.text = TextRenderer()
        self.scoreboard = ScoreBoard()

        self._scenes = {
            "menu": MenuScene(self),
            "play": PlayScene(self),
            "result": ResultScene(self),
        }
        self._current_scene = self._scenes["menu"]

    def change_scene(self, name):
        self._current_scene = self._scenes[name]
        self._current_scene.on_enter()

    def quit(self):
        pygame.quit()
        sys.exit()

    def run(self):
        while True:

            dt = self._clock.tick(Settings.FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                self._current_scene.handle_event(event)

            self._current_scene.update(dt)

            self._screen.fill(Settings.BG)
            self._current_scene.draw(self._screen)
            pygame.display.flip()


if __name__ == "__main__":
    Game().run()