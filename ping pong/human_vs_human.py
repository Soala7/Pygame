import pygame
import sys

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
RED = (255, 100, 100)
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 90
BALL_SIZE = 15
PADDLE_SPEED = 7
BALL_SPEED_X = 7
BALL_SPEED_Y = 7

class Paddle:
    def __init__(self, x, y, color=WHITE):
        self.x = x
        self.y = y
        self.speed = PADDLE_SPEED
        self.color = color
    
    def move_up(self):
        if self.y > 0:
            self.y -= self.speed
    
    def move_down(self):
        if self.y < HEIGHT - PADDLE_HEIGHT:
            self.y += self.speed
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT))

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed_x = BALL_SPEED_X
        self.speed_y = BALL_SPEED_Y
    
    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Bounce off top and bottom walls
        if self.y <= 0 or self.y >= HEIGHT - BALL_SIZE:
            self.speed_y = -self.speed_y
    
    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed_x = -self.speed_x  # Change direction
    
    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, BALL_SIZE, BALL_SIZE))

def run_human_vs_human():
    screen = pygame.display.get_surface()
    if screen is None:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    pygame.display.set_caption("Ping Pong - Human vs Human")
    clock = pygame.time.Clock()
    
    # Create game objects
    left_paddle = Paddle(20, HEIGHT // 2 - PADDLE_HEIGHT // 2, BLUE)
    right_paddle = Paddle(WIDTH - 35, HEIGHT // 2 - PADDLE_HEIGHT // 2, RED)
    ball = Ball(WIDTH // 2, HEIGHT // 2)
    
    # Score
    left_score = 0
    right_score = 0
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)
    
    # Game state
    game_paused = True
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return  # Return to main menu instead of quitting
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_paused = False
                elif event.key == pygame.K_r:
                    # Reset game
                    left_score = 0
                    right_score = 0
                    ball.reset()
                    game_paused = True
                elif event.key == pygame.K_ESCAPE:
                    return  # Return to main menu
        
        if not game_paused:
            # Handle input
            keys = pygame.key.get_pressed()
            
            # Left paddle controls (W/S)
            if keys[pygame.K_w]:
                left_paddle.move_up()
            if keys[pygame.K_s]:
                left_paddle.move_down()
            
            # Right paddle controls (UP/DOWN arrows)
            if keys[pygame.K_UP]:
                right_paddle.move_up()
            if keys[pygame.K_DOWN]:
                right_paddle.move_down()
            
            # Move ball
            ball.move()
            
            # Ball collision with paddles
            # Left paddle collision
            if (ball.x <= left_paddle.x + PADDLE_WIDTH and 
                ball.y + BALL_SIZE >= left_paddle.y and 
                ball.y <= left_paddle.y + PADDLE_HEIGHT):
                ball.speed_x = -ball.speed_x
            
            # Right paddle collision
            if (ball.x + BALL_SIZE >= right_paddle.x and 
                ball.y + BALL_SIZE >= right_paddle.y and 
                ball.y <= right_paddle.y + PADDLE_HEIGHT):
                ball.speed_x = -ball.speed_x
            
            # Score points
            if ball.x < 0:
                right_score += 1
                ball.reset()
            elif ball.x > WIDTH:
                left_score += 1
                ball.reset()
        
        # Clear screen
        screen.fill(BLACK)
        
        # Draw center line
        for i in range(0, HEIGHT, 20):
            pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 2, i, 4, 10))
        
        # Draw game objects
        left_paddle.draw(screen)
        right_paddle.draw(screen)
        ball.draw(screen)
        
        # Draw scores
        left_text = font.render(str(left_score), True, BLUE)
        right_text = font.render(str(right_score), True, RED)
        screen.blit(left_text, (WIDTH // 4, 50))
        screen.blit(right_text, (3 * WIDTH // 4, 50))
        
        # Draw player labels
        left_label = small_font.render("PLAYER 1", True, BLUE)
        right_label = small_font.render("PLAYER 2", True, RED)
        screen.blit(left_label, (WIDTH // 4 - 50, 100))
        screen.blit(right_label, (3 * WIDTH // 4 - 50, 100))
        
        # Draw instructions
        if game_paused:
            pause_text = font.render("PRESS SPACE TO START", True, WHITE)
            text_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(pause_text, text_rect)
            
            control1_text = small_font.render("Player 1: W/S keys", True, BLUE)
            control1_rect = control1_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
            screen.blit(control1_text, control1_rect)
            
            control2_text = small_font.render("Player 2: UP/DOWN arrows", True, RED)
            control2_rect = control2_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
            screen.blit(control2_text, control2_rect)
            
            back_text = small_font.render("ESC: Back to Menu | R: Reset", True, WHITE)
            back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 140))
            screen.blit(back_text, back_rect)
        
        # Check for game over
        if left_score >= 10 or right_score >= 10:
            winner = "PLAYER 1 WINS!" if left_score >= 10 else "PLAYER 2 WINS!"
            winner_color = BLUE if left_score >= 10 else RED
            win_text = font.render(winner, True, winner_color)
            win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(win_text, win_rect)
            
            play_again_text = small_font.render("Press R to play again", True, WHITE)
            play_again_rect = play_again_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            screen.blit(play_again_text, play_again_rect)
            
            game_paused = True
        
        pygame.display.flip()
        clock.tick(60)