import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Bird properties
BIRD_WIDTH = 30
BIRD_HEIGHT = 30
BIRD_X = 50
GRAVITY = 0.5
JUMP_STRENGTH = -8

# Pipe properties
PIPE_WIDTH = 60
PIPE_GAP = 150
PIPE_SPEED = 3

class Bird:
    def __init__(self):
        self.x = BIRD_X
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.rect = pygame.Rect(self.x, self.y, BIRD_WIDTH, BIRD_HEIGHT)
    
    def jump(self):
        self.velocity = JUMP_STRENGTH
    
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.y = self.y
    
    def draw(self, screen):
        pygame.draw.ellipse(screen, YELLOW, self.rect)
        # Add a simple eye
        eye_x = self.x + BIRD_WIDTH // 2 + 5
        eye_y = self.y + BIRD_HEIGHT // 2 - 3
        pygame.draw.circle(screen, BLACK, (int(eye_x), int(eye_y)), 3)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - 100)
        self.top_rect = pygame.Rect(x, 0, PIPE_WIDTH, self.height)
        self.bottom_rect = pygame.Rect(x, self.height + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - self.height - PIPE_GAP)
        self.passed = False
    
    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x
    
    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.top_rect)
        pygame.draw.rect(screen, GREEN, self.bottom_rect)
        # Add pipe caps
        cap_height = 20
        top_cap = pygame.Rect(self.x - 5, self.height - cap_height, PIPE_WIDTH + 10, cap_height)
        bottom_cap = pygame.Rect(self.x - 5, self.height + PIPE_GAP, PIPE_WIDTH + 10, cap_height)
        pygame.draw.rect(screen, GREEN, top_cap)
        pygame.draw.rect(screen, GREEN, bottom_cap)
    
    def collides_with(self, bird):
        return bird.rect.colliderect(self.top_rect) or bird.rect.colliderect(self.bottom_rect)
    
    def is_off_screen(self):
        return self.x + PIPE_WIDTH < 0

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset_game()
    
    def reset_game(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.game_started = False
        # Add initial pipes
        for i in range(3):
            self.pipes.append(Pipe(SCREEN_WIDTH + i * 200))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.game_over:
                        if not self.game_started:
                            self.game_started = True
                        self.bird.jump()
                    else:
                        self.reset_game()
        return True
    
    def update(self):
        if not self.game_started or self.game_over:
            return
        
        # Update bird
        self.bird.update()
        
        # Check if bird hits ground or ceiling
        if self.bird.y + BIRD_HEIGHT > SCREEN_HEIGHT or self.bird.y < 0:
            self.game_over = True
        
        # Update pipes
        for pipe in self.pipes[:]:
            pipe.update()
            
            # Check collision
            if pipe.collides_with(self.bird):
                self.game_over = True
            
            # Check if bird passed pipe
            if not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.x:
                pipe.passed = True
                self.score += 1
            
            # Remove off-screen pipes
            if pipe.is_off_screen():
                self.pipes.remove(pipe)
        
        # Add new pipes
        if len(self.pipes) < 3:
            last_pipe_x = self.pipes[-1].x if self.pipes else SCREEN_WIDTH
            if last_pipe_x < SCREEN_WIDTH:
                self.pipes.append(Pipe(last_pipe_x + 200))
    
    def draw(self):
        # Draw background
        self.screen.fill(BLUE)
        
        # Draw clouds (simple white circles)
        for i in range(3):
            x = (i * 150 + 50) % (SCREEN_WIDTH + 100)
            y = 50 + i * 30
            pygame.draw.circle(self.screen, WHITE, (x, y), 20, 0)
            pygame.draw.circle(self.screen, WHITE, (x + 15, y), 15, 0)
            pygame.draw.circle(self.screen, WHITE, (x - 15, y), 15, 0)
        
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)
        
        # Draw bird
        self.bird.draw(self.screen)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw instructions or game over
        if not self.game_started:
            title_text = self.font.render("Flappy Bird", True, WHITE)
            instruction_text = pygame.font.Font(None, 24).render("Press SPACE to start", True, WHITE)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(title_text, title_rect)
            self.screen.blit(instruction_text, instruction_rect)
        
        if self.game_over:
            game_over_text = self.font.render("Game Over!", True, RED)
            restart_text = pygame.font.Font(None, 24).render("Press SPACE to restart", True, WHITE)
            final_score_text = pygame.font.Font(None, 24).render(f"Final Score: {self.score}", True, WHITE)
            
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))
            
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(restart_text, restart_rect)
            self.screen.blit(final_score_text, final_score_rect)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()