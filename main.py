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
GRID_COLOR = (40, 40, 40)
BASE_FPS = 10
MAX_FPS = 30
FADE_SPEED = 5  

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption("Snake Game")

class Settings:
    def __init__(self):
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.done = False
        self.q = False
        self.score = 0

class Snake:
    def __init__(self, settings):
        self.settings = settings
        self.width = GRID_SIZE
        self.height = GRID_SIZE
        self.direction = Direction.RIGHT
        self.body = [(GRID_WIDTH // 4, GRID_HEIGHT // 2)]
        self.color = SNAKE_COLOR
        self.grow_next_move = False
        self.alpha = 255  

    def draw(self, surface):
        for segment in self.body:
            pygame.draw.rect(
                surface,
                (*self.color[:3], self.alpha),  
                pygame.Rect(
                    segment[0] * GRID_SIZE,
                    segment[1] * GRID_SIZE,
                    GRID_SIZE - 1,
                    GRID_SIZE - 1
                )
            )

    def fade_out(self):
        self.alpha = max(0, self.alpha - FADE_SPEED)
        return self.alpha > 0

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
        self.color = APPLE_COLOR
        self.x = 0
        self.y = 0
        self.respawn()

    def respawn(self):
        snake_positions = set(self.settings.snake.body)
        max_attempts = 50  
        
        for _ in range(max_attempts):
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in snake_positions:
                self.x, self.y = x, y
                return True
                
        total_cells = GRID_WIDTH * GRID_HEIGHT
        if len(snake_positions) >= total_cells:
            return False
            
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if (x, y) not in snake_positions:
                    self.x, self.y = x, y
                    return True
        return False

class Game_Over:
    def __init__(self, settings):
        self.settings = settings
        self.color = GAME_OVER_COLOR
        self.font = pygame.font.Font(None, 36)
        self.text_surfaces = []
        self.text_rects = []
        self.update_text("Game Over\nScore: 0")

    def update_text(self, text):
        self.text_surfaces.clear()  
        self.text_rects.clear()     
        
        lines = text.split('\n')
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
        self.settings.snake = self.player
        self.apple = Apple(self.settings)
        self.game_over = Game_Over(self.settings)
        self.high_score = 0
        self.current_fps = BASE_FPS
        self.is_fading = False
        self.start_time = time.time()
        self.game_time = 0
        
        self.direction_keys = {
            (pygame.K_UP, pygame.K_w): Direction.UP,
            (pygame.K_DOWN, pygame.K_s): Direction.DOWN,
            (pygame.K_LEFT, pygame.K_a): Direction.LEFT,
            (pygame.K_RIGHT, pygame.K_d): Direction.RIGHT
        }

    def process_input(self):
        keys = pygame.key.get_pressed()
        
        for key_pair, direction in self.direction_keys.items():
            if keys[key_pair[0]] or keys[key_pair[1]]:
                self.player.change_direction(direction)
                break

    def update_game_time(self):
        if not self.settings.done:
            self.game_time = int(time.time() - self.start_time)

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def reset_game(self):
        self.settings.score = 0
        self.settings.q = False
        self.settings.done = False
        self.player = Snake(self.settings)
        self.settings.snake = self.player
        self.player.alpha = 255
        self.apple = Apple(self.settings)
        self.current_fps = BASE_FPS
        self.is_fading = False
        self.start_time = time.time()
        self.game_time = 0
        self.game_over.update_text("Game Over\nScore: 0")

    def update_speed(self):
        self.current_fps = min(BASE_FPS + self.settings.score // 20, MAX_FPS)

    def draw_grid(self):
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.settings.screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.settings.screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))

    def quit(self):
        self.settings.done = True
        if self.settings.score > self.high_score:
            self.high_score = self.settings.score
        self.game_over.update_text(
            f"Game Over\nScore: {self.settings.score}\n"
            f"Time: {self.format_time(self.game_time)}\n"
            f"High Score: {self.high_score}"
        )

    def run(self):
        running = True
        while running:
            while not self.settings.q and not self.settings.done:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.settings.q = True
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.settings.q = True
                            running = False
                        elif event.key == pygame.K_SPACE:
                            self.reset_game()

                self.process_input()
                self.update_game_time()

                if not self.player.move():
                    self.is_fading = True
                    self.quit()
                    continue

                self.settings.screen.fill((0, 0, 0))
                self.draw_grid()
                
                if (self.player.body[0][0] == self.apple.x and 
                    self.player.body[0][1] == self.apple.y):
                    self.settings.score += 10
                    self.player.grow()
                    if not self.apple.respawn():
                        self.quit()
                    self.update_speed()

                self.player.draw(self.settings.screen)
                
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

                score_text = self.game_over.font.render(
                    f"Score: {self.settings.score} | High Score: {self.high_score} | Time: {self.format_time(self.game_time)}", 
                    True, 
                    (255, 255, 255)
                )
                self.settings.screen.blit(score_text, (10, 10))

                pygame.display.flip()
                clock.tick(self.current_fps)

            while self.settings.done and not self.settings.q:
                self.settings.screen.fill((0, 0, 0))
                self.draw_grid()
                
                if self.is_fading:
                    if self.player.fade_out():
                        self.player.draw(self.settings.screen)
                    else:
                        self.is_fading = False

                for i, surface in enumerate(self.game_over.text_surfaces):
                    self.settings.screen.blit(surface, self.game_over.text_rects[i])
                
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.settings.q = True
                            running = False
                        elif event.key == pygame.K_SPACE:
                            self.reset_game()
                            break  
                    elif event.type == pygame.QUIT:
                        self.settings.q = True
                        running = False

                pygame.display.flip()
                clock.tick(BASE_FPS)

            if self.settings.q:
                running = False

game = Game()
game.run()
