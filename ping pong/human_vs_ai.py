import pygame
import sys
import random

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 100, 100)
BLUE = (100, 100, 255)
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

class AIPlayer:
    def __init__(self, paddle, difficulty=0.75):
        self.paddle = paddle
        self.difficulty = difficulty  # 0.0 to 1.0, higher = better AI
        self.reaction_delay = 0
        self.target_y = paddle.y
    
    def update(self, ball):
        # Add some reaction delay and imperfection to make AI beatable
        self.reaction_delay += 1
        
        # Only update target every few frames to simulate reaction time
        if self.reaction_delay > 3:
            self.reaction_delay = 0
            
            # Predict where ball will be when it reaches paddle
            if ball.speed_x > 0:  # Ball moving toward AI
                # Calculate intersection point
                time_to_reach = (self.paddle.x - ball.x) / ball.speed_x
                predicted_y = ball.y + ball.speed_y * time_to_reach
                
                # Add some randomness based on difficulty
                error_margin = (1 - self.difficulty) * 100
                predicted_y += random.uniform(-error_margin, error_margin)
                
                self.target_y = predicted_y - PADDLE_HEIGHT // 2
            else:
                # Ball moving away, move toward center
                self.target_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        
        # Move paddle toward target position
        paddle_center = self.paddle.y + PADDLE_HEIGHT // 2
        target_center = self.target_y + PADDLE_HEIGHT // 2
        
        # AI movement speed (slightly slower than max for realism)
        ai_speed = self.paddle.speed * 0.8
        
        if paddle_center < target_center - 10:
            if self.paddle.y < HEIGHT - PADDLE_HEIGHT:
                self.paddle.y += min(ai_speed, target_center - paddle_center)
        elif paddle_center > target_center + 10:
            if self.paddle.y > 0:
                self.paddle.y -= min(ai_speed, paddle_center - target_center)

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed_x = BALL_SPEED_X
        self.speed_y = BALL_SPEED_Y
        self.max_speed = 12
    
    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Bounce off top and bottom walls
        if self.y <= 0 or self.y >= HEIGHT - BALL_SIZE:
            self.speed_y = -self.speed_y
    
    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        # Randomize initial direction
        self.speed_x = BALL_SPEED_X if random.choice([True, False]) else -BALL_SPEED_X
        self.speed_y = random.uniform(-BALL_SPEED_Y, BALL_SPEED_Y)
    
    def speed_up(self):
        # Slightly increase ball speed after paddle hits (up to max)
        if abs(self.speed_x) < self.max_speed:
            self.speed_x *= 1.05
        if abs(self.speed_y) < self.max_speed:
            self.speed_y *= 1.02
    
    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, BALL_SIZE, BALL_SIZE))

def run_human_vs_ai():
    screen = pygame.display.get_surface()
    if screen is None:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    pygame.display.set_caption("Ping Pong - Human vs AI")
    clock = pygame.time.Clock()
    
    # Create game objects
    player_paddle = Paddle(20, HEIGHT // 2 - PADDLE_HEIGHT // 2, BLUE)
    ai_paddle = Paddle(WIDTH - 35, HEIGHT // 2 - PADDLE_HEIGHT // 2, RED)
    ball = Ball(WIDTH // 2, HEIGHT // 2)
    
    # Create AI player
    ai_player = AIPlayer(ai_paddle, difficulty=0.75)  # Adjustable difficulty
    
    # Score
    player_score = 0
    ai_score = 0
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
                    player_score = 0
                    ai_score = 0
                    ball.reset()
                    game_paused = True
                elif event.key == pygame.K_ESCAPE:
                    return  # Return to main menu
        
        if not game_paused:
            # Handle player input
            keys = pygame.key.get_pressed()
            
            # Player paddle controls (W/S or UP/DOWN)
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                player_paddle.move_up()
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                player_paddle.move_down()
            
            # Update AI
            ai_player.update(ball)
            
            # Move ball
            ball.move()
            
            # Ball collision with paddles
            # Player paddle collision
            if (ball.x <= player_paddle.x + PADDLE_WIDTH and 
                ball.y + BALL_SIZE >= player_paddle.y and 
                ball.y <= player_paddle.y + PADDLE_HEIGHT and
                ball.speed_x < 0):
                ball.speed_x = -ball.speed_x
                # Add some spin based on where ball hits paddle
                hit_pos = (ball.y - player_paddle.y) / PADDLE_HEIGHT
                ball.speed_y = (hit_pos - 0.5) * 10
                ball.speed_up()
            
            # AI paddle collision
            if (ball.x + BALL_SIZE >= ai_paddle.x and 
                ball.y + BALL_SIZE >= ai_paddle.y and 
                ball.y <= ai_paddle.y + PADDLE_HEIGHT and
                ball.speed_x > 0):
                ball.speed_x = -ball.speed_x
                # Add some spin based on where ball hits paddle
                hit_pos = (ball.y - ai_paddle.y) / PADDLE_HEIGHT
                ball.speed_y = (hit_pos - 0.5) * 10
                ball.speed_up()
            
            # Score points
            if ball.x < 0:
                ai_score += 1
                ball.reset()
            elif ball.x > WIDTH:
                player_score += 1
                ball.reset()
        
        # Clear screen
        screen.fill(BLACK)
        
        # Draw center line
        for i in range(0, HEIGHT, 20):
            pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 2, i, 4, 10))
        
        # Draw game objects
        player_paddle.draw(screen)
        ai_paddle.draw(screen)
        ball.draw(screen)
        
        # Draw scores
        player_text = font.render(str(player_score), True, BLUE)
        ai_text = font.render(str(ai_score), True, RED)
        screen.blit(player_text, (WIDTH // 4, 50))
        screen.blit(ai_text, (3 * WIDTH // 4, 50))
        
        # Draw labels
        player_label = small_font.render("PLAYER", True, BLUE)
        ai_label = small_font.render("AI", True, RED)
        screen.blit(player_label, (WIDTH // 4 - 40, 100))
        screen.blit(ai_label, (3 * WIDTH // 4 - 20, 100))
        
        # Draw instructions
        if game_paused:
            pause_text = font.render("PRESS SPACE TO START", True, WHITE)
            text_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(pause_text, text_rect)
            
            control_text = small_font.render("Controls: W/S or UP/DOWN arrows", True, WHITE)
            control_rect = control_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
            screen.blit(control_text, control_rect)
            
            back_text = small_font.render("ESC: Back to Menu | R: Reset", True, WHITE)
            back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
            screen.blit(back_text, back_rect)
        
        # Check for game over
        if player_score >= 10 or ai_score >= 10:
            winner = "PLAYER WINS!" if player_score >= 10 else "AI WINS!"
            winner_color = BLUE if player_score >= 10 else RED
            win_text = font.render(winner, True, winner_color)
            win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(win_text, win_rect)
            
            play_again_text = small_font.render("Press R to play again", True, WHITE)
            play_again_rect = play_again_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            screen.blit(play_again_text, play_again_rect)
            
            game_paused = True
        
        pygame.display.flip()
        clock.tick(60)
