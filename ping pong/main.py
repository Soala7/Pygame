import pygame
import sys
from human_vs_human import run_human_vs_human
from human_vs_ai import run_human_vs_ai

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
GREEN = (100, 255, 150)
RED = (255, 100, 100)
FPS = 60

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong - Main Menu")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 50)
medium_font = pygame.font.Font(None, 36)

def draw_menu():
    screen.fill(BLACK)
    
    # Title with gradient effect
    title = font.render("PING PONG", True, WHITE)
    title_rect = title.get_rect(center=(WIDTH//2, 120))
    screen.blit(title, title_rect)
    
    # Subtitle
    subtitle = medium_font.render("Choose Your Game Mode", True, (200, 200, 200))
    subtitle_rect = subtitle.get_rect(center=(WIDTH//2, 170))
    screen.blit(subtitle, subtitle_rect)
    
    # Human vs Human button
    hvh_rect = pygame.Rect(WIDTH//2 - 200, 240, 400, 80)
    pygame.draw.rect(screen, BLUE, hvh_rect)
    pygame.draw.rect(screen, WHITE, hvh_rect, 3)
    human_text = small_font.render("Human vs Human", True, WHITE)
    human_rect = human_text.get_rect(center=hvh_rect.center)
    screen.blit(human_text, human_rect)
    
    # Human vs AI button
    hai_rect = pygame.Rect(WIDTH//2 - 200, 340, 400, 80)
    pygame.draw.rect(screen, GREEN, hai_rect)
    pygame.draw.rect(screen, WHITE, hai_rect, 3)
    ai_text = small_font.render("Human vs AI", True, WHITE)
    ai_rect = ai_text.get_rect(center=hai_rect.center)
    screen.blit(ai_text, ai_rect)
    
    # Quit button
    quit_rect = pygame.Rect(WIDTH//2 - 200, 440, 400, 80)
    pygame.draw.rect(screen, RED, quit_rect)
    pygame.draw.rect(screen, WHITE, quit_rect, 3)
    quit_text = small_font.render("Quit Game", True, WHITE)
    quit_text_rect = quit_text.get_rect(center=quit_rect.center)
    screen.blit(quit_text, quit_text_rect)
    
    # Instructions
    inst_text = medium_font.render("Click on a button to start!", True, (150, 150, 150))
    inst_rect = inst_text.get_rect(center=(WIDTH//2, 550))
    screen.blit(inst_text, inst_rect)
    
    return hvh_rect, hai_rect, quit_rect

def main():
    print("Starting Ping Pong Game...")
    print("Main menu loaded successfully!")
    
    while True:
        hvh_rect, hai_rect, quit_rect = draw_menu()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quitting game...")
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Human vs Human button
                if hvh_rect.collidepoint(mouse_pos):
                    print("Starting Human vs Human mode...")
                    try:
                        run_human_vs_human()
                        print("Returned from Human vs Human mode")
                    except Exception as e:
                        print(f"Error in Human vs Human mode: {e}")
                
                # Human vs AI button
                elif hai_rect.collidepoint(mouse_pos):
                    print("Starting Human vs AI mode...")
                    try:
                        run_human_vs_ai()
                        print("Returned from Human vs AI mode")
                    except Exception as e:
                        print(f"Error in Human vs AI mode: {e}")
                
                # Quit button
                elif quit_rect.collidepoint(mouse_pos):
                    print("Quitting game...")
                    pygame.quit()
                    sys.exit()
            
            # Keyboard shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    print("Starting Human vs Human mode (keyboard shortcut)...")
                    try:
                        run_human_vs_human()
                    except Exception as e:
                        print(f"Error in Human vs Human mode: {e}")
                elif event.key == pygame.K_2:
                    print("Starting Human vs AI mode (keyboard shortcut)...")
                    try:
                        run_human_vs_ai()
                    except Exception as e:
                        print(f"Error in Human vs AI mode: {e}")
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    print("Quitting game...")
                    pygame.quit()
                    sys.exit()
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()