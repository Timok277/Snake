import pygame
import random
from enum import Enum
import time

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
SNAKE_COLOR = (0, 255, 0)
APPLE_COLOR = (255, 0, 0)
GAME_OVER_COLOR = (255, 100, 0)
BASE_FPS = 10
MAX_FPS = 30

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

pygame.init()
clock = pygame.time.Clock()

class Settings:
    def __init__(self):
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.done = False
        self.q = False
        self.score = 0
        self.player_speed = self.width / 180
        self.bullet_speed = self.width / 120

class Snake:
    def __init__(self, settings):
        self.settings = settings
        self.width = GRID_SIZE
        self.height = GRID_SIZE
        self.direction = Direction.RIGHT
        self.body = [(GRID_WIDTH // 4, GRID_HEIGHT // 2)]
        self.color = SNAKE_COLOR
        self.grow_next_move = False

    def move(self):
        new_head = (
            self.body[0][0] + self.direction.value[0],
            self.body[0][1] + self.direction.value[1]
        )
        
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            return False

        if new_head in self.body[:-1]:
            return False

        self.body.insert(0, new_head)
        if not self.grow_next_move:
            self.body.pop()
        else:
            self.grow_next_move = False
        return True

    def grow(self):
        self.grow_next_move = True

    def change_direction(self, new_direction):
        if (self.direction == Direction.UP and new_direction == Direction.DOWN or
            self.direction == Direction.DOWN and new_direction == Direction.UP or
            self.direction == Direction.LEFT and new_direction == Direction.RIGHT or
            self.direction == Direction.RIGHT and new_direction == Direction.LEFT):
            return
        self.direction = new_direction

class Apple:
    def __init__(self, settings):
        self.settings = settings
        self.width = GRID_SIZE
        self.height = GRID_SIZE
        self.respawn()
        self.color = APPLE_COLOR

    def respawn(self):
        self.x = random.randint(0, GRID_WIDTH - 1)
        self.y = random.randint(0, GRID_HEIGHT - 1)

class Game_Over:
    def __init__(self, settings):
        self.settings = settings
        self.color = GAME_OVER_COLOR
        self.font = pygame.font.Font(None, 36)
        self.update_text("Game Over\nScore: 0")

    def update_text(self, text):
        lines = text.split('\n')
        self.text_surfaces = []
        self.text_rects = []
        
        for i, line in enumerate(lines):
            surface = self.font.render(line, True, self.color)
            rect = surface.get_rect()
            rect.center = (self.settings.width // 2, 
                         self.settings.height // 2 - (len(lines) - 1) * 20 + i * 40)
            self.text_surfaces.append(surface)
            self.text_rects.append(rect)

class Game:
    def __init__(self):
        self.settings = Settings()
        self.player = Snake(self.settings)
        self.apple = Apple(self.settings)
        self.game_over = Game_Over(self.settings)
        self.high_score = 0
        self.current_fps = BASE_FPS
        self.pressed_keys = []

    def handle_key_press(self, key):
        if key in [pygame.K_UP, pygame.K_w]:
            if Direction.UP not in self.pressed_keys:
                self.pressed_keys.append(Direction.UP)
        elif key in [pygame.K_DOWN, pygame.K_s]:
            if Direction.DOWN not in self.pressed_keys:
                self.pressed_keys.append(Direction.DOWN)
        elif key in [pygame.K_LEFT, pygame.K_a]:
            if Direction.LEFT not in self.pressed_keys:
                self.pressed_keys.append(Direction.LEFT)
        elif key in [pygame.K_RIGHT, pygame.K_d]:
            if Direction.RIGHT not in self.pressed_keys:
                self.pressed_keys.append(Direction.RIGHT)

    def handle_key_release(self, key):
        if key in [pygame.K_UP, pygame.K_w]:
            if Direction.UP in self.pressed_keys:
                self.pressed_keys.remove(Direction.UP)
        elif key in [pygame.K_DOWN, pygame.K_s]:
            if Direction.DOWN in self.pressed_keys:
                self.pressed_keys.remove(Direction.DOWN)
        elif key in [pygame.K_LEFT, pygame.K_a]:
            if Direction.LEFT in self.pressed_keys:
                self.pressed_keys.remove(Direction.LEFT)
        elif key in [pygame.K_RIGHT, pygame.K_d]:
            if Direction.RIGHT in self.pressed_keys:
                self.pressed_keys.remove(Direction.RIGHT)

    def process_direction(self):
        if not self.pressed_keys:
            return

        new_direction = self.pressed_keys[-1]
        self.player.change_direction(new_direction)

    def quit(self):
        self.settings.done = True
        if self.settings.score > self.high_score:
            self.high_score = self.settings.score
        self.game_over.update_text(f"Game Over\nScore: {self.settings.score}\nHigh Score: {self.high_score}")

    def reset_game(self):
        self.settings.score = 0
        self.settings.q = False
        self.settings.done = False
        self.player = Snake(self.settings)
        self.apple = Apple(self.settings)
        self.current_fps = BASE_FPS
        self.game_over.update_text("Game Over\nScore: 0")
        self.pressed_keys.clear()

    def update_speed(self):
        self.current_fps = min(BASE_FPS + self.settings.score // 20, MAX_FPS)

    def run(self):
        while not self.settings.q and not self.settings.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.settings.q = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.settings.q = True
                    elif event.key == pygame.K_SPACE:
                        self.reset_game()
                    else:
                        self.handle_key_press(event.key)
                elif event.type == pygame.KEYUP:
                    self.handle_key_release(event.key)

            self.process_direction()

            if not self.player.move():
                self.quit()
                continue

            self.settings.screen.fill((0, 0, 0))
            
            for segment in self.player.body:
                pygame.draw.rect(
                    self.settings.screen,
                    self.player.color,
                    pygame.Rect(
                        segment[0] * GRID_SIZE,
                        segment[1] * GRID_SIZE,
                        GRID_SIZE - 1,
                        GRID_SIZE - 1
                    )
                )

            pygame.draw.rect(
                self.settings.screen,
                self.apple.color,
                pygame.Rect(
                    self.apple.x * GRID_SIZE,
                    self.apple.y * GRID_SIZE,
                    GRID_SIZE - 1,
                    GRID_SIZE - 1
                )
            )

            if (self.player.body[0][0] == self.apple.x and 
                self.player.body[0][1] == self.apple.y):
                self.settings.score += 10
                self.player.grow()
                self.apple.respawn()
                while (self.apple.x, self.apple.y) in self.player.body:
                    self.apple.respawn()
                self.update_speed()

            score_text = self.game_over.font.render(
                f"Score: {self.settings.score} | High Score: {self.high_score}", 
                True, 
                (255, 255, 255)
            )
            self.settings.screen.blit(score_text, (10, 10))

            pygame.display.flip()
            clock.tick(self.current_fps)

        while self.settings.done and not self.settings.q:
            self.settings.screen.fill((0, 0, 0))
            for i, surface in enumerate(self.game_over.text_surfaces):
                self.settings.screen.blit(surface, self.game_over.text_rects[i])
            
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.settings.q = True
                    elif event.key == pygame.K_SPACE:
                        self.reset_game()
                        self.run()
                elif event.type == pygame.QUIT:
                    self.settings.q = True

            pygame.display.flip()
            clock.tick(BASE_FPS)
 
game = Game()
game.run()
