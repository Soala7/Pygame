import pygame
import random
import sys
import os

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 400
CAR_WIDTH, CAR_HEIGHT = 20, 40
OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 20, 40
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CAR_COLORS = [(0, 0, 255), (0, 255, 0), (255, 255, 0)]
OBSTACLE_COLORS = [(255, 0, 0), (255, 165, 0), (128, 0, 128)]
ROAD_GRAY = (50, 50, 50)

# Game settings
BASE_SPAWN_RATE = 0.02
SPAWN_RATE_INCREASE = 0.002
BASE_SPEED = 4
SPEED_INCREASE_INTERVAL = 10

class CarDodgeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Car Dodge Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        self.high_score = self.load_high_score()
        self.reset_game()

    def reset_game(self):
        self.car = pygame.Rect(
            SCREEN_WIDTH // 2 - CAR_WIDTH // 2,
            SCREEN_HEIGHT - CAR_HEIGHT - 20,
            CAR_WIDTH,
            CAR_HEIGHT
        )
        self.car_color = random.choice(CAR_COLORS)
        self.obstacles = []
        self.score = 0
        self.game_over = False

    def load_high_score(self):
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r") as f:
                return int(f.read())
        return 0

    def save_high_score(self):
        with open("highscore.txt", "w") as f:
            f.write(str(self.high_score))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.car.left > 0:
            self.car.x -= 5
        if keys[pygame.K_RIGHT] and self.car.right < SCREEN_WIDTH:
            self.car.x += 5

    def update_game(self):
        spawn_rate = BASE_SPAWN_RATE + (self.score * SPAWN_RATE_INCREASE)
        if random.random() < spawn_rate:
            obstacle = pygame.Rect(
                random.randrange(0, SCREEN_WIDTH - OBSTACLE_WIDTH, OBSTACLE_WIDTH),
                -OBSTACLE_HEIGHT,
                OBSTACLE_WIDTH,
                OBSTACLE_HEIGHT
            )
            color = random.choice(OBSTACLE_COLORS)
            self.obstacles.append((obstacle, color))

        for obs, color in self.obstacles[:]:
            obs.y += BASE_SPEED + (self.score // SPEED_INCREASE_INTERVAL)
            if obs.top > SCREEN_HEIGHT:
                self.obstacles.remove((obs, color))
                self.score += 1
            elif self.car.colliderect(obs):
                self.game_over = True
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()

    def draw(self):
        self.screen.fill(ROAD_GRAY)

        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH // 2 - 2, y, 4, 20))

        pygame.draw.rect(self.screen, self.car_color, self.car)

        for obs, color in self.obstacles:
            pygame.draw.rect(self.screen, color, obs)

        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        high_score_text = self.font.render(f'High Score: {self.high_score}', True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(high_score_text, (10, 40))

        pygame.display.flip()

    def show_game_over_screen(self):
        self.screen.fill(BLACK)
        game_over_text = self.font.render("Game Over!", True, WHITE)
        retry_text = self.font.render("Press R to Retry or Q to Quit", True, WHITE)
        score_text = self.font.render(f"Your Score: {self.score}", True, WHITE)

        self.screen.blit(game_over_text, (100, 120))
        self.screen.blit(score_text, (100, 160))
        self.screen.blit(retry_text, (30, 220))
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        waiting = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

    def run(self):
        running = True
        while running:
            running = self.handle_events()

            if not self.game_over:
                self.handle_input()
                self.update_game()
                self.draw()
            else:
                self.show_game_over_screen()

            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = CarDodgeGame()
    game.run()
